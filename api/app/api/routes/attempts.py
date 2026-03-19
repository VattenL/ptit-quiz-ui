from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import random

from app.db.session import get_db
from app.core.deps import get_current_user, require_roles
from app.models.models import User, Quiz, Question, QuizAttempt, AttemptAnswer
from app.schemas.quiz import AttemptSubmit, AttemptOut

router = APIRouter(prefix="/attempts", tags=["Attempts"])


# POST /attempts/start — bắt đầu làm bài
@router.post("/start", status_code=201)
def start_attempt(
    body: dict,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    quiz_id = body.get("quiz_id")
    quiz = db.query(Quiz).options(joinedload(Quiz.questions)).filter(Quiz.id == quiz_id).first()
    if not quiz or quiz.status.value != "published":
        raise HTTPException(404, "Quiz not found or not available")

    now = datetime.utcnow()
    if quiz.available_from and now < quiz.available_from:
        raise HTTPException(400, "Quiz not yet available")
    if quiz.available_until and now > quiz.available_until:
        raise HTTPException(400, "Quiz has expired")

    attempt_count = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.status != "in_progress",
    ).count()
    if attempt_count >= quiz.max_attempts:
        raise HTTPException(400, f"Maximum attempts ({quiz.max_attempts}) reached")

    # Expire any stale attempt
    stale = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.status == "in_progress",
    ).first()
    if stale:
        stale.status = "timed_out"
        stale.submitted_at = now

    question_ids = [q.id for q in quiz.questions]
    if quiz.shuffle_questions:
        random.shuffle(question_ids)

    attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_id=current_user.id,
        question_order=question_ids,
        total_marks=quiz.total_marks,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    question_map = {q.id: q for q in quiz.questions}
    questions_out = []
    for qid in question_ids:
        q = question_map[qid]
        options = [
            {"id": o.id, "content": o.content, "order_index": o.order_index}
            for o in sorted(q.options, key=lambda x: x.order_index)
        ]
        if quiz.shuffle_options:
            random.shuffle(options)
        questions_out.append({
            "id": q.id, "content": q.content, "type": q.type.value,
            "marks": q.marks, "image_url": q.image_url, "options": options,
        })

    return {
        "attempt_id": attempt.id,
        "quiz_id": quiz_id,
        "time_limit_mins": quiz.time_limit_mins,
        "started_at": attempt.started_at,
        "questions": questions_out,
    }


# POST /attempts/{id}/submit — nộp bài + chấm điểm tự động
@router.post("/{attempt_id}/submit")
def submit_attempt(
    attempt_id: str,
    body: AttemptSubmit,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    attempt = db.query(QuizAttempt).options(
        joinedload(QuizAttempt.quiz).joinedload(Quiz.questions).joinedload(Question.options)
    ).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.student_id == current_user.id,
    ).first()

    if not attempt:
        raise HTTPException(404, "Attempt not found")
    if attempt.status.value != "in_progress":
        raise HTTPException(400, "Attempt already submitted")

    now = datetime.utcnow()
    time_spent = int((now - attempt.started_at).total_seconds())

    question_map = {q.id: q for q in attempt.quiz.questions}
    option_map = {o.id: o for q in attempt.quiz.questions for o in q.options}

    total_score = 0.0
    for ans in body.answers:
        question = question_map.get(ans.question_id)
        if not question:
            continue

        is_correct, marks_awarded = False, 0.0

        if question.type.value in ("single_choice", "true_false"):
            selected_id = (ans.selected_options or [None])[0]
            opt = option_map.get(selected_id) if selected_id else None
            is_correct = bool(opt and opt.is_correct)
            marks_awarded = question.marks if is_correct else 0.0

        elif question.type.value == "multiple_choice":
            correct_ids  = {o.id for o in question.options if o.is_correct}
            selected_ids = set(ans.selected_options or [])
            is_correct   = selected_ids == correct_ids
            if is_correct:
                marks_awarded = question.marks
            elif selected_ids and selected_ids.issubset(correct_ids):
                marks_awarded = round(question.marks * len(selected_ids) / len(correct_ids), 2)

        elif question.type.value == "short_answer":
            is_correct, marks_awarded = None, 0.0

        total_score += marks_awarded
        db.merge(AttemptAnswer(
            attempt_id=attempt_id, question_id=ans.question_id,
            selected_options=ans.selected_options, text_answer=ans.text_answer,
            is_correct=is_correct, marks_awarded=marks_awarded,
        ))

    percentage = round((total_score / attempt.total_marks) * 100, 2) if attempt.total_marks else 0
    attempt.status       = "submitted"
    attempt.submitted_at = now
    attempt.time_spent_secs = time_spent
    attempt.score        = round(total_score, 2)
    attempt.percentage   = percentage
    attempt.passed       = percentage >= attempt.quiz.pass_score
    db.commit()
    db.refresh(attempt)

    return {
        "attempt_id": attempt.id,
        "score": attempt.score,
        "total_marks": attempt.total_marks,
        "percentage": attempt.percentage,
        "passed": attempt.passed,
        "time_spent_secs": attempt.time_spent_secs,
    }


# GET /attempts/{id} — chi tiết một lần làm bài
@router.get("/{attempt_id}", response_model=AttemptOut)
def get_attempt(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(404, "Attempt not found")
    if current_user.role == "student" and attempt.student_id != current_user.id:
        raise HTTPException(403, "Forbidden")
    return AttemptOut.model_validate(attempt)
