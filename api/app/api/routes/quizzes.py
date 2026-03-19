from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import asc, desc
from typing import Optional

from app.db.session import get_db
from app.core.deps import get_current_user, require_roles
from app.models.models import User, Quiz, Question, QuestionOption
from app.schemas.quiz import (
    QuizCreate, QuizUpdate, QuizCreateResponse,
    QuizListResponse, QuizSummary, QuizDetail, QuestionOut,
    QuestionCreate, SortRequest,
)

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


# GET /quizzes — danh sách đề, filter + phân trang
@router.get("", response_model=QuizListResponse)
def list_quizzes(
    course_id: Optional[str] = Query(None),
    status:    Optional[str] = Query(None),
    page:      int           = Query(1,      ge=1),
    limit:     int           = Query(20,     ge=1, le=100),
    sort_by:   str           = Query("created_at", pattern="^(created_at|title|total_marks|time_limit_mins)$"),
    order:     str           = Query("desc",        pattern="^(asc|desc)$"),
    current_user: User       = Depends(get_current_user),
    db: Session              = Depends(get_db),
):
    q = db.query(Quiz)
    if current_user.role == "student":
        q = q.filter(Quiz.status == "published")
    elif status:
        q = q.filter(Quiz.status == status)
    if course_id:
        q = q.filter(Quiz.course_id == course_id)

    sort_col = getattr(Quiz, sort_by)
    q = q.order_by(desc(sort_col) if order == "desc" else asc(sort_col))

    total   = q.count()
    quizzes = q.offset((page - 1) * limit).limit(limit).all()

    return QuizListResponse(
        quizzes=[
            QuizSummary(
                quiz_id=qz.id, title=qz.title, description=qz.description,
                course_id=qz.course_id, status=qz.status.value,
                time_limit_mins=qz.time_limit_mins, total_marks=qz.total_marks,
                created_at=qz.created_at,
            ) for qz in quizzes
        ],
        total=total, page=page, limit=limit,
    )


# POST /quizzes — tạo đề mới
@router.post("", response_model=QuizCreateResponse, status_code=201)
def create_quiz(
    body: QuizCreate,
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    quiz = Quiz(**body.model_dump(), created_by=current_user.id)
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return QuizCreateResponse(quiz_id=quiz.id, created_at=quiz.created_at)


# GET /quizzes/{id} — chi tiết đề + câu hỏi
@router.get("/{quiz_id}", response_model=QuizDetail)
def get_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = (
        db.query(Quiz)
        .options(joinedload(Quiz.questions).joinedload(Question.options))
        .filter(Quiz.id == quiz_id)
        .first()
    )
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    if current_user.role == "student" and quiz.status.value != "published":
        raise HTTPException(403, "Quiz not available")

    return QuizDetail(
        quiz_id=quiz.id, title=quiz.title, description=quiz.description,
        course_id=quiz.course_id, status=quiz.status.value,
        time_limit_mins=quiz.time_limit_mins, shuffle_questions=quiz.shuffle_questions,
        shuffle_options=quiz.shuffle_options, pass_score=quiz.pass_score,
        max_attempts=quiz.max_attempts, available_from=quiz.available_from,
        available_until=quiz.available_until, total_marks=quiz.total_marks,
        created_at=quiz.created_at,
        questions=[
            QuestionOut(
                id=q.id, content=q.content, type=q.type.value,
                marks=q.marks, explanation=q.explanation,
                order_index=q.order_index, image_url=q.image_url,
                options=[
                    {"id": o.id, "content": o.content, "is_correct": o.is_correct,
                     "order_index": o.order_index, "image_url": o.image_url}
                    for o in sorted(q.options, key=lambda x: x.order_index)
                ]
            )
            for q in sorted(quiz.questions, key=lambda x: x.order_index)
        ],
    )


# PATCH /quizzes/{id} — cập nhật đề
@router.patch("/{quiz_id}")
def update_quiz(
    quiz_id: str,
    body: QuizUpdate,
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    if current_user.role == "teacher" and quiz.created_by != current_user.id:
        raise HTTPException(403, "Not your quiz")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(quiz, field, value)
    db.commit()
    return {"success": True, "quiz_id": quiz.id}


# DELETE /quizzes/{id} — xóa đề
@router.delete("/{quiz_id}")
def delete_quiz(
    quiz_id: str,
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    if current_user.role == "teacher" and quiz.created_by != current_user.id:
        raise HTTPException(403, "Not your quiz")
    db.delete(quiz)
    db.commit()
    return {"success": True}


# POST /quizzes/{id}/questions — thêm câu hỏi
@router.post("/{quiz_id}/questions", status_code=201)
def add_question(
    quiz_id: str,
    body: QuestionCreate,
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(404, "Quiz not found")

    question = Question(
        quiz_id=quiz_id, content=body.content, type=body.type,
        marks=body.marks, explanation=body.explanation,
        order_index=body.order_index, image_url=body.image_url,
    )
    db.add(question)
    db.flush()

    for opt in body.options:
        db.add(QuestionOption(
            question_id=question.id, content=opt.content,
            is_correct=opt.is_correct, order_index=opt.order_index,
            image_url=opt.image_url,
        ))

    quiz.total_marks = sum(q.marks for q in quiz.questions) + question.marks
    db.commit()
    db.refresh(question)
    return {"question_id": question.id, "quiz_id": quiz_id}


# PATCH /quizzes/{id}/questions/{qid} — cập nhật câu hỏi
@router.patch("/{quiz_id}/questions/{question_id}")
def update_question(
    quiz_id: str,
    question_id: str,
    body: "QuestionUpdateBody",
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    from app.schemas.quiz import QuestionUpdate
    question = db.query(Question).filter(
        Question.id == question_id, Question.quiz_id == quiz_id
    ).first()
    if not question:
        raise HTTPException(404, "Question not found")

    data = body.model_dump(exclude_none=True)
    options_data = data.pop("options", None)

    for field, value in data.items():
        setattr(question, field, value)

    if options_data is not None:
        # Replace all options
        for o in question.options:
            db.delete(o)
        db.flush()
        for opt in options_data:
            db.add(QuestionOption(
                question_id=question.id, content=opt["content"],
                is_correct=opt.get("is_correct", False),
                order_index=opt.get("order_index", 0),
                image_url=opt.get("image_url"),
            ))

    # Recalculate total_marks
    db.flush()
    quiz = question.quiz
    quiz.total_marks = sum(q.marks for q in quiz.questions)
    db.commit()
    return {"success": True, "question_id": question_id}


# DELETE /quizzes/{id}/questions/{qid} — xóa câu hỏi
@router.delete("/{quiz_id}/questions/{question_id}")
def delete_question(
    quiz_id: str,
    question_id: str,
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    question = db.query(Question).filter(
        Question.id == question_id, Question.quiz_id == quiz_id
    ).first()
    if not question:
        raise HTTPException(404, "Question not found")

    quiz = question.quiz
    db.delete(question)
    db.flush()
    quiz.total_marks = sum(q.marks for q in quiz.questions if q.id != question_id)
    db.commit()
    return {"success": True}


# POST /quizzes/{id}/sort — sắp xếp thứ tự câu hỏi
@router.post("/{quiz_id}/sort")
def sort_questions(
    quiz_id: str,
    body: SortRequest,
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    question_map = {q.id: q for q in questions}
    for item in body.order:
        if item.question_id in question_map:
            question_map[item.question_id].order_index = item.index
    db.commit()
    return {"success": True}


from app.schemas.quiz import QuestionUpdate
QuestionUpdateBody = QuestionUpdate
