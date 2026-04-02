from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from schemas.quiz import (
    QuizListResponse, QuizCreateInput, QuizCreateResponse,
    QuizUpdateInput, QuizDetailResponse, SortInput, SuccessResponse
)
import services.quiz as quiz_service

router = APIRouter(prefix="/api/quizzes", tags=["Quizzes"])


@router.get("", response_model=QuizListResponse)
def get_quizzes(
    course_id : Optional[str] = Query(None),
    status    : Optional[str] = Query(None),
    page      : int           = Query(1, ge=1),
    limit     : int           = Query(10, ge=1, le=100),
    db        : Session       = Depends(get_db),
):
    return quiz_service.get_quizzes(db, course_id=course_id, status=status, page=page, limit=limit)


@router.post("", response_model=QuizCreateResponse, status_code=201)
def create_quiz(body: QuizCreateInput, db: Session = Depends(get_db)):
    return quiz_service.create_quiz(db, data=body.dict())


@router.get("/search")
def search_quizzes(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return quiz_service.search_quizzes(db, search_term=q)


@router.get("/search_id/{quiz_id}", response_model=QuizDetailResponse)
def get_quiz(quiz_id: str, db: Session = Depends(get_db)):
    return quiz_service.get_quiz_by_id(db, quiz_id=quiz_id)


@router.put("/{quiz_id}", response_model=SuccessResponse)
def update_quiz(quiz_id: str, body: QuizUpdateInput, db: Session = Depends(get_db)):
    return quiz_service.update_quiz(db, quiz_id=quiz_id, data=body.dict())


@router.delete("/{quiz_id}", response_model=SuccessResponse)
def delete_quiz(quiz_id: str, db: Session = Depends(get_db)):
    return quiz_service.delete_quiz(db, quiz_id=quiz_id)
