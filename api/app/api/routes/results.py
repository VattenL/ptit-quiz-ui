from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.deps import get_current_user, require_roles
from app.models.models import User, Quiz, QuizAttempt
from app.schemas.quiz import StudentResultsResponse, StudentResult, AttemptOut

router = APIRouter(prefix="/results", tags=["Results"])


# GET /results — thống kê tổng (admin/teacher), filter theo course_id hoặc student_id
@router.get("")
def get_results(
    course_id:  Optional[str] = Query(None),
    student_id: Optional[str] = Query(None),
    quiz_id:    Optional[str] = Query(None),
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    q = db.query(QuizAttempt).join(Quiz).filter(QuizAttempt.status == "submitted")
    if course_id:
        q = q.filter(Quiz.course_id == course_id)
    if student_id:
        q = q.filter(QuizAttempt.student_id == student_id)
    if quiz_id:
        q = q.filter(QuizAttempt.quiz_id == quiz_id)

    attempts = q.all()
    if not attempts:
        return {"average_score": None, "pass_rate": None, "total_attempts": 0, "attempts": []}

    scores      = [a.percentage for a in attempts if a.percentage is not None]
    average     = round(sum(scores) / len(scores), 2) if scores else None
    pass_rate   = round(sum(1 for a in attempts if a.passed) / len(attempts) * 100, 2)

    return {
        "average_score": average,
        "pass_rate": pass_rate,
        "total_attempts": len(attempts),
        "attempts": [AttemptOut.model_validate(a) for a in attempts],
    }


# GET /results/me — kết quả của sinh viên đang đăng nhập
@router.get("/me", response_model=StudentResultsResponse)
def my_results(
    course_id: Optional[str] = Query(None),
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    q = db.query(QuizAttempt).join(Quiz).filter(
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.status == "submitted",
    )
    if course_id:
        q = q.filter(Quiz.course_id == course_id)
    attempts = q.order_by(QuizAttempt.submitted_at.desc()).all()

    return StudentResultsResponse(results=[
        StudentResult(
            quiz_id=a.quiz_id, title=a.quiz.title,
            score=a.score, total_marks=a.total_marks,
            percentage=a.percentage, passed=a.passed,
            attempted_at=a.submitted_at or a.started_at,
        ) for a in attempts
    ])


# GET /results/students/{student_id} — kết quả của một sinh viên cụ thể
@router.get("/students/{student_id}", response_model=StudentResultsResponse)
def student_results(
    student_id: str,
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(404, "Student not found")

    attempts = db.query(QuizAttempt).join(Quiz).filter(
        QuizAttempt.student_id == student_id,
        QuizAttempt.status == "submitted",
    ).order_by(QuizAttempt.submitted_at.desc()).all()

    return StudentResultsResponse(results=[
        StudentResult(
            quiz_id=a.quiz_id, title=a.quiz.title,
            score=a.score, total_marks=a.total_marks,
            percentage=a.percentage, passed=a.passed,
            attempted_at=a.submitted_at or a.started_at,
        ) for a in attempts
    ])


# GET /results/quizzes/{quiz_id}/stats — thống kê theo đề thi
@router.get("/quizzes/{quiz_id}/stats")
def quiz_stats(
    quiz_id: str,
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(404, "Quiz not found")

    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.status == "submitted",
    ).all()

    scores    = [a.percentage for a in attempts if a.percentage is not None]
    average   = round(sum(scores) / len(scores), 2) if scores else None
    pass_rate = round(sum(1 for a in attempts if a.passed) / len(attempts) * 100, 2) if attempts else None

    return {
        "quiz_id": quiz_id,
        "title": quiz.title,
        "average_score": average,
        "pass_rate": pass_rate,
        "total_attempts": len(attempts),
        "attempts": [AttemptOut.model_validate(a) for a in attempts],
    }
