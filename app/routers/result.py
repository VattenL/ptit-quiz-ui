from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from schemas.result import ResultsResponse, StudentResultsResponse
import services.result as result_service

router = APIRouter(prefix="/api/results", tags=["Results"])


@router.get("", response_model=ResultsResponse)
def get_results(
    course_id  : Optional[str] = Query(None),
    student_id : Optional[str] = Query(None),
    db         : Session       = Depends(get_db),
):
    return result_service.get_results(db, course_id=course_id, student_id=student_id)


@router.get("/students/{student_id}", response_model=StudentResultsResponse)
def get_student_results(student_id: str, db: Session = Depends(get_db)):
    return result_service.get_student_results(db, student_id=student_id)
