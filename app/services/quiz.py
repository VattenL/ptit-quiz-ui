from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
import uuid

from app.models.quiz import Quiz


def get_quizzes(db: Session, course_id=None, status=None, page=1, limit=10):
    query = db.query(Quiz)
    if course_id: 
        query = query.filter(Quiz.course_id == course_id)
    if status:    
        query = query.filter(Quiz.status == status)
    total   = query.count()
    offset  = (page - 1) * limit
    quizzes = query.offset(offset).limit(limit).all()
    return {"quizzes": quizzes, "total": total, "page": page}

def create_quiz(db: Session, data: dict):
    quiz = Quiz(id=str(uuid.uuid4()), created_at=datetime.utcnow(), **data)
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return {"quiz_id": quiz.id, "created_at": quiz.created_at}

def get_quiz_by_id(db: Session, quiz_id: str):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz: 
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

def update_quiz(db: Session, quiz_id: str, data: dict):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz: raise HTTPException(404)
    for key, value in data.items():
           if value is not None: setattr(quiz, key, value)
    quiz.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(quiz)
    return {"success": True}

def delete_quiz(db: Session, quiz_id: str):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz: raise HTTPException(404)
    db.delete(quiz)
    db.commit()
    return {"success": True}

def sort_quizzes(db: Session, quiz_ids: list):
    quizzes = []
    for quiz_id in quiz_ids:
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if quiz:
            quizzes.append(quiz)
    return {"success": True}
