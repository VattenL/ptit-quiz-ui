from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.db.session import get_db
from app.core.deps import get_current_user, require_roles
from app.models.models import User, Course, CourseEnrollment

router = APIRouter(prefix="/courses", tags=["Courses"])


class CourseCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    faculty_id: Optional[str] = None


class CourseOut(BaseModel):
    id: str
    name: str
    code: str
    description: Optional[str] = None
    faculty_id: Optional[str] = None
    teacher_id: Optional[str] = None
    is_active: bool
    model_config = {"from_attributes": True}


class EnrollRequest(BaseModel):
    student_id: str


@router.get("", response_model=List[CourseOut])
def list_courses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Course).filter(Course.is_active == True)
    if current_user.role == "student":
        enrolled_ids = [e.course_id for e in
                        db.query(CourseEnrollment).filter(CourseEnrollment.student_id == current_user.id)]
        q = q.filter(Course.id.in_(enrolled_ids))
    return [CourseOut.model_validate(c) for c in q.offset((page - 1) * limit).limit(limit).all()]


@router.post("", response_model=CourseOut, status_code=201)
def create_course(
    body: CourseCreate,
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    if db.query(Course).filter(Course.code == body.code).first():
        raise HTTPException(400, "Course code already exists")
    course = Course(
        **body.model_dump(),
        teacher_id=current_user.id if current_user.role == "teacher" else None,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return CourseOut.model_validate(course)


@router.post("/{course_id}/enroll")
def enroll_student(
    course_id: str,
    body: EnrollRequest,
    current_user: User = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    if not db.query(Course).filter(Course.id == course_id).first():
        raise HTTPException(404, "Course not found")
    if db.query(CourseEnrollment).filter_by(course_id=course_id, student_id=body.student_id).first():
        raise HTTPException(400, "Already enrolled")
    db.add(CourseEnrollment(course_id=course_id, student_id=body.student_id))
    db.commit()
    return {"success": True}
