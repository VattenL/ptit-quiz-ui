"""
Tạo tất cả bảng trong database.
Chạy: python create_tables.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.db.session import engine, Base
from app.models.models import (  # noqa: import all so SQLAlchemy sees them
    Faculty, User, TokenBlacklist, Course, CourseEnrollment,
    Quiz, Question, QuestionOption, QuizAttempt, AttemptAnswer,
)

Base.metadata.create_all(bind=engine)
print("✅ Tất cả bảng đã được tạo:")
for t in Base.metadata.sorted_tables:
    print(f"   • {t.name}")
