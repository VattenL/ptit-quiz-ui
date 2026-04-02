from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import HTTPException
from datetime import datetime
import uuid

from models.quiz import Quiz


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
    cnt = db.execute(select(func.count(Quiz.id))).scalar()
    quiz = Quiz(id=str(cnt + 1), created_at=datetime.utcnow(), **data)
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return {"quiz_id": quiz.id, "created_at": quiz.created_at}

def get_quiz_by_id(db: Session, quiz_id: str):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz: 
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Map the ORM 'id' to 'quiz_id' to satisfy the Pydantic schema validation
    return {
        "quiz_id": quiz.id,
        "title": quiz.title,
        "time_limit_mins": quiz.time_limit_mins,
        "total_marks": quiz.total_marks,
        "questions": quiz.questions
    }

def update_quiz(db: Session, quiz_id: str, data: dict):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz: 
        raise HTTPException(status_code=404, detail="Quiz not found")
    for key, value in data.items():
           if value is not None: setattr(quiz, key, value)
    quiz.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(quiz)
    return quiz

def delete_quiz(db: Session, quiz_id: str):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz: 
        raise HTTPException(status_code=404, detail="Quiz not found")
    db.delete(quiz)
    db.commit()
    return {"success": True}

def search_quizzes(db: Session, search_term: str):
    quizzes = db.query(Quiz).filter(Quiz.title.ilike(f"%{search_term.strip()}%")).all()
    if not quizzes: 
        raise HTTPException(status_code=404, detail="Quiz not found")
    return {"success": True, "quizzes": quizzes}
