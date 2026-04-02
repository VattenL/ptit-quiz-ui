import uuid
import random
from datetime import datetime, timedelta

from core.database import SessionLocal, engine
from models.quiz import (
    Base, Faculty, User, Course, CourseEnrollment, Quiz,
    Question, QuestionOption, QuizAttempt, AttemptAnswer, TokenBlacklist
)

def create_seed_data():
    db = SessionLocal()
    
    try:
        # Check if database already has data
        if db.query(Faculty).first():
            print("Database already contains data, skipping seed...")
            return

        print("Generating mock data...")

        # 1. Faculties
        faculties = []
        for i in range(20):
            faculty = Faculty(
                id=i + 1,
                name=f"Faculty of Science {i+1}",
                code=f"FSC{i+1}",
                created_at=datetime.utcnow() - timedelta(days=random.randint(100, 1000))
            )
            faculties.append(faculty)
        db.add_all(faculties)
        
        # 2. Users (Mix of roles: admin, teacher, student)
        users = []
        roles = ["admin", "teacher", "student"]
        for i in range(20):
            user = User(
                id=i + 1,
                name=f"User {i+1}",
                email=f"user{i+1}@example.com",
                password_hash="hashed_password",
                role=random.choice(roles),
                faculty_id=random.choice(faculties).id,
                avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={i}",
                language="en",
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(10, 100)),
                updated_at=datetime.utcnow()
            )
            users.append(user)
        db.add_all(users)
        
        teachers = [u for u in users if u.role == "teacher"] or users
        students = [u for u in users if u.role == "student"] or users

        # 3. Courses
        courses = []
        for i in range(20):
            course = Course(
                id=i + 1,
                name=f"Introduction to Programming {i+1}",
                code=f"CS10{i+1}",
                description="A foundational course for programming.",
                faculty_id=random.choice(faculties).id,
                teacher_id=random.choice(teachers).id,
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 200)),
                updated_at=datetime.utcnow()
            )
            courses.append(course)
        db.add_all(courses)

        # 4. CourseEnrollments
        enrollments = []
        for i in range(20):
            enrollment = CourseEnrollment(
                id=i + 1,
                course_id=random.choice(courses).id,
                student_id=random.choice(students).id,
                enrolled_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            enrollments.append(enrollment)
        db.add_all(enrollments)

        # 5. Quizzes
        quizzes = []
        for i in range(20):
            quiz = Quiz(
                id=i + 1,
                title=f"Midterm Exam {i+1}",
                description="Solve all questions carefully.",
                course_id=random.choice(courses).id,
                created_by=random.choice(teachers).id,
                time_limit_mins=60,
                shuffle_questions=True,
                shuffle_options=True,
                status=random.choice(["draft", "published"]),
                pass_score=50.0,
                max_attempts=random.choice([1, 2, 3]),
                available_from=datetime.utcnow() - timedelta(days=2),
                available_until=datetime.utcnow() + timedelta(days=5),
                total_marks=100.0,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
                updated_at=datetime.utcnow()
            )
            quizzes.append(quiz)
        db.add_all(quizzes)

        # 6. Questions
        questions = []
        types = ["multiple_choice", "true_false", "short_answer"]
        for i in range(20):
            question = Question(
                id=i + 1,
                quiz_id=random.choice(quizzes).id,
                content=f"What is the output of 2 + {i}?",
                type=random.choice(types),
                marks=5.0,
                explanation="Basic arithmetic.",
                order_index=i,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            questions.append(question)
        db.add_all(questions)

        # 7. QuestionOptions
        options = []
        for i in range(20):
            option = QuestionOption(
                id=i + 1,
                question_id=random.choice(questions).id,
                content=f"Option {i+1}",
                is_correct=random.choice([True, False]),
                order_index=i % 4
            )
            options.append(option)
        db.add_all(options)

        # 8. QuizAttempts
        attempts = []
        for i in range(20):
            status = random.choice(["in_progress", "submitted", "graded"])
            attempt = QuizAttempt(
                id=i + 1,
                quiz_id=random.choice(quizzes).id,
                student_id=random.choice(students).id,
                status=status,
                started_at=datetime.utcnow() - timedelta(hours=1),
                submitted_at=datetime.utcnow() if status != "in_progress" else None,
                time_spent_secs=3600,
                score=random.uniform(30.0, 100.0) if status == "graded" else 0.0,
                total_marks=100.0,
                percentage=random.uniform(30.0, 100.0) if status == "graded" else 0.0,
                passed=random.choice([True, False]),
                question_order=["q1", "q2"], # mock
                created_at=datetime.utcnow() - timedelta(hours=2)
            )
            attempts.append(attempt)
        db.add_all(attempts)

        # 9. AttemptAnswers
        answers = []
        for i in range(20):
            answer = AttemptAnswer(
                id=i + 1,
                attempt_id=random.choice(attempts).id,
                question_id=random.choice(questions).id,
                selected_options=[str(uuid.uuid4())],
                text_answer=f"Answer text {i+1}",
                is_correct=random.choice([True, False]),
                marks_awarded=random.uniform(0.0, 5.0),
                answered_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 60))
            )
            answers.append(answer)
        db.add_all(answers)

        # 10. TokenBlacklist
        blacklists = []
        for i in range(20):
            blacklist = TokenBlacklist(
                id=i + 1,
                token=f"invalidated_jwt_token_{i}",
                user_id=random.choice(users).id,
                expires_at=datetime.utcnow() + timedelta(days=1),
                created_at=datetime.utcnow()
            )
            blacklists.append(blacklist)
        db.add_all(blacklists)

        db.commit()
        print("Successfully seeded database with 20 rows each for 10 tables.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data()