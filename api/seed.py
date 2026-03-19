"""
Seed dữ liệu mẫu cho quiz platform.
Chạy: python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.db.session import SessionLocal, engine, Base
from app.models.models import (
    Faculty, User, Course, CourseEnrollment,
    Quiz, Question, QuestionOption,
    UserRole, QuizStatus, QuestionType,
)
from app.core.security import hash_password
from datetime import datetime, timedelta


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # ── Faculties ──────────────────────────────────
        faculties_data = [
            ("Công nghệ Thông tin", "CNTT"),
            ("Kinh tế",             "KT"),
            ("Kỹ thuật Điện",       "KTD"),
        ]
        for name, code in faculties_data:
            if not db.query(Faculty).filter_by(code=code).first():
                db.add(Faculty(name=name, code=code))
        db.flush()

        cntt = db.query(Faculty).filter_by(code="CNTT").first()

        # ── Users ──────────────────────────────────────
        users_data = [
            dict(name="Admin System",   email="admin@quiz.vn",    password="admin123",   role=UserRole.admin),
            dict(name="Nguyễn Giảng",   email="teacher@quiz.vn",  password="teacher123", role=UserRole.teacher, faculty_id=cntt.id),
            dict(name="Trần Sinh Viên", email="student@quiz.vn",  password="student123", role=UserRole.student, faculty_id=cntt.id),
            dict(name="Lê Văn An",      email="student2@quiz.vn", password="student123", role=UserRole.student, faculty_id=cntt.id),
        ]
        for ud in users_data:
            if not db.query(User).filter_by(email=ud["email"]).first():
                db.add(User(
                    name=ud["name"],
                    email=ud["email"],
                    password_hash=hash_password(ud["password"]),
                    role=ud["role"],
                    faculty_id=ud.get("faculty_id"),
                ))
        db.flush()

        teacher  = db.query(User).filter_by(email="teacher@quiz.vn").first()
        student  = db.query(User).filter_by(email="student@quiz.vn").first()
        student2 = db.query(User).filter_by(email="student2@quiz.vn").first()

        # ── Course ─────────────────────────────────────
        course = db.query(Course).filter_by(code="CNTT101").first()
        if not course:
            course = Course(
                name="Nhập môn Lập trình",
                code="CNTT101",
                description="Học Python cơ bản",
                faculty_id=cntt.id,
                teacher_id=teacher.id,
            )
            db.add(course)
            db.flush()

        # Enroll students
        for s in [student, student2]:
            if not db.query(CourseEnrollment).filter_by(course_id=course.id, student_id=s.id).first():
                db.add(CourseEnrollment(course_id=course.id, student_id=s.id))

        # ── Quiz 1: Python cơ bản ──────────────────────
        quiz1 = db.query(Quiz).filter_by(title="Kiểm tra Python cơ bản").first()
        if not quiz1:
            quiz1 = Quiz(
                title="Kiểm tra Python cơ bản",
                description="Bài kiểm tra 5 câu hỏi về Python",
                course_id=course.id,
                created_by=teacher.id,
                time_limit_mins=30,
                shuffle_questions=True,
                shuffle_options=True,
                status=QuizStatus.published,
                pass_score=60.0,
                max_attempts=2,
                available_from=datetime.utcnow() - timedelta(days=1),
                available_until=datetime.utcnow() + timedelta(days=30),
            )
            db.add(quiz1)
            db.flush()

            questions_data = [
                {
                    "content": "Python là ngôn ngữ lập trình thuộc loại nào?",
                    "type": QuestionType.single_choice, "marks": 1.0, "order_index": 0,
                    "options": [
                        ("Biên dịch (Compiled)",          False),
                        ("Thông dịch (Interpreted)",      True),
                        ("Hợp ngữ (Assembly)",            False),
                        ("Ngôn ngữ máy (Machine)",        False),
                    ]
                },
                {
                    "content": "Câu lệnh nào in ra 'Hello World' đúng cú pháp Python?",
                    "type": QuestionType.single_choice, "marks": 1.0, "order_index": 1,
                    "options": [
                        ('print("Hello World")',          True),
                        ('echo "Hello World"',            False),
                        ('console.log("Hello World")',    False),
                        ('printf("Hello World")',         False),
                    ]
                },
                {
                    "content": "Kiểu dữ liệu nào là IMMUTABLE trong Python? (chọn tất cả đúng)",
                    "type": QuestionType.multiple_choice, "marks": 2.0, "order_index": 2,
                    "options": [
                        ("tuple", True),
                        ("list",  False),
                        ("str",   True),
                        ("dict",  False),
                    ]
                },
                {
                    "content": "Python hỗ trợ lập trình hướng đối tượng (OOP).",
                    "type": QuestionType.true_false, "marks": 1.0, "order_index": 3,
                    "options": [
                        ("True",  True),
                        ("False", False),
                    ]
                },
                {
                    "content": "Hàm nào dùng để lấy độ dài của một list trong Python?",
                    "type": QuestionType.single_choice, "marks": 1.0, "order_index": 4,
                    "options": [
                        ("size()",   False),
                        ("count()",  False),
                        ("len()",    True),
                        ("length()", False),
                    ]
                },
            ]

            total = 0.0
            for qd in questions_data:
                q = Question(
                    quiz_id=quiz1.id,
                    content=qd["content"],
                    type=qd["type"],
                    marks=qd["marks"],
                    order_index=qd["order_index"],
                )
                db.add(q)
                db.flush()
                for idx, (text, correct) in enumerate(qd["options"]):
                    db.add(QuestionOption(
                        question_id=q.id,
                        content=text,
                        is_correct=correct,
                        order_index=idx,
                    ))
                total += qd["marks"]
            quiz1.total_marks = total

        # ── Quiz 2: Draft (chưa publish) ───────────────
        quiz2 = db.query(Quiz).filter_by(title="Kiểm tra cuối kỳ - Draft").first()
        if not quiz2:
            quiz2 = Quiz(
                title="Kiểm tra cuối kỳ - Draft",
                description="Đề thi đang soạn thảo",
                course_id=course.id,
                created_by=teacher.id,
                time_limit_mins=60,
                status=QuizStatus.draft,
                pass_score=50.0,
                max_attempts=1,
            )
            db.add(quiz2)
            db.flush()

            q = Question(
                quiz_id=quiz2.id,
                content="Câu hỏi mẫu trong đề draft",
                type=QuestionType.single_choice,
                marks=1.0,
                order_index=0,
            )
            db.add(q)
            db.flush()
            db.add(QuestionOption(question_id=q.id, content="Đáp án A", is_correct=True,  order_index=0))
            db.add(QuestionOption(question_id=q.id, content="Đáp án B", is_correct=False, order_index=1))
            quiz2.total_marks = 1.0

        db.commit()
        print("✅ Seed hoàn tất!")
        print()
        print("  Tài khoản mẫu:")
        print("  ┌─────────────────────────┬──────────────┬─────────┐")
        print("  │ Email                   │ Password     │ Role    │")
        print("  ├─────────────────────────┼──────────────┼─────────┤")
        print("  │ admin@quiz.vn           │ admin123     │ admin   │")
        print("  │ teacher@quiz.vn         │ teacher123   │ teacher │")
        print("  │ student@quiz.vn         │ student123   │ student │")
        print("  │ student2@quiz.vn        │ student123   │ student │")
        print("  └─────────────────────────┴──────────────┴─────────┘")
        print()
        print("  Chạy server: uvicorn app.main:app --reload --port 8000")
        print("  Swagger UI : http://localhost:8000/docs")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
