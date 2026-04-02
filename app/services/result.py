from sqlalchemy.orm import Session
from models.quiz import QuizAttempt, Quiz


def get_results(db: Session, course_id=None, student_id=None):
    
    
    query = db.query(QuizAttempt)
    if student_id: 
        query = query.filter(QuizAttempt.student_id == student_id)
    if course_id:  
        query = query.join(Quiz).filter(Quiz.course_id == course_id)
    attempts = query.all()
    if not attempts: 
        return {"average_score": 0, "pass_rate": 0, "attempts": []}
    average_score = sum(a.score or 0 for a in attempts) / len(attempts)
    pass_rate     = sum(1 for a in attempts if a.passed) / len(attempts)
    mapped_attempts = [
        {
            "id": str(a.id),
            "quiz_id": str(a.quiz_id),
            "student_id": str(a.student_id),
            "score": a.score,
            "total_marks": a.total_marks,
            "percentage": a.percentage,
            "passed": a.passed,
            "attempted_at": a.created_at
        }
        for a in attempts
    ]
    return {"average_score": average_score, "pass_rate": pass_rate, "attempts": mapped_attempts}



def get_student_results(db: Session, student_id: str):
    attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).all()
    results = []
    for attempt in attempts:
           quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
           results.append({
               "quiz_id":      attempt.quiz_id,
               "title":        quiz.title if quiz else "Unknown",
               "score":        attempt.score,
               "passed":       attempt.passed,
               "attempted_at": attempt.created_at,
           })
    return {"results": results}

