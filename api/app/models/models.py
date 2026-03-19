import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float,
    DateTime, ForeignKey, Enum, JSON, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
import enum

from app.db.session import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


# ─── ENUMS ───────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    admin   = "admin"
    teacher = "teacher"
    student = "student"


class QuizStatus(str, enum.Enum):
    draft     = "draft"
    published = "published"
    archived  = "archived"


class QuestionType(str, enum.Enum):
    single_choice   = "single_choice"
    multiple_choice = "multiple_choice"
    true_false      = "true_false"
    short_answer    = "short_answer"


class AttemptStatus(str, enum.Enum):
    in_progress = "in_progress"
    submitted   = "submitted"
    timed_out   = "timed_out"


# ─── FACULTY ─────────────────────────────────────────────────

class Faculty(Base):
    __tablename__ = "faculties"

    id         = Column(CHAR(36), primary_key=True, default=gen_uuid)
    name       = Column(String(255), nullable=False)
    code       = Column(String(50),  unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    users   = relationship("User",   back_populates="faculty")
    courses = relationship("Course", back_populates="faculty")


# ─── USER ────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id             = Column(CHAR(36), primary_key=True, default=gen_uuid)
    name           = Column(String(255), nullable=False)
    email          = Column(String(255), unique=True, nullable=False, index=True)
    password_hash  = Column(Text, nullable=True)
    role           = Column(Enum(UserRole), nullable=False, default=UserRole.student)
    faculty_id     = Column(CHAR(36), ForeignKey("faculties.id", ondelete="SET NULL"), nullable=True)
    avatar         = Column(Text, nullable=True)
    language       = Column(String(10), default="vi")
    oauth_provider = Column(String(50),  nullable=True)
    oauth_id       = Column(String(255), nullable=True)
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    faculty     = relationship("Faculty",          back_populates="users")
    enrollments = relationship("CourseEnrollment", back_populates="student")
    attempts    = relationship("QuizAttempt",      back_populates="student")
    quizzes     = relationship("Quiz",             back_populates="created_by_user")

    __table_args__ = (Index("idx_users_role", "role"),)


# ─── TOKEN BLACKLIST ─────────────────────────────────────────

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id         = Column(CHAR(36), primary_key=True, default=gen_uuid)
    token      = Column(Text,     nullable=False)
    user_id    = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"))
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_token_bl_expires", "expires_at"),)


# ─── COURSE ──────────────────────────────────────────────────

class Course(Base):
    __tablename__ = "courses"

    id          = Column(CHAR(36), primary_key=True, default=gen_uuid)
    name        = Column(String(255), nullable=False)
    code        = Column(String(50),  unique=True, nullable=False)
    description = Column(Text, nullable=True)
    faculty_id  = Column(CHAR(36), ForeignKey("faculties.id", ondelete="SET NULL"), nullable=True)
    teacher_id  = Column(CHAR(36), ForeignKey("users.id",     ondelete="SET NULL"), nullable=True)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    faculty     = relationship("Faculty",          back_populates="courses")
    enrollments = relationship("CourseEnrollment", back_populates="course")
    quizzes     = relationship("Quiz",             back_populates="course")

    __table_args__ = (
        Index("idx_courses_faculty", "faculty_id"),
        Index("idx_courses_teacher", "teacher_id"),
    )


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    id          = Column(CHAR(36), primary_key=True, default=gen_uuid)
    course_id   = Column(CHAR(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    student_id  = Column(CHAR(36), ForeignKey("users.id",   ondelete="CASCADE"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    course  = relationship("Course", back_populates="enrollments")
    student = relationship("User",   back_populates="enrollments")

    __table_args__ = (
        UniqueConstraint("course_id", "student_id"),
        Index("idx_enroll_course",  "course_id"),
        Index("idx_enroll_student", "student_id"),
    )


# ─── QUIZ ────────────────────────────────────────────────────

class Quiz(Base):
    __tablename__ = "quizzes"

    id                = Column(CHAR(36), primary_key=True, default=gen_uuid)
    title             = Column(String(255), nullable=False)
    description       = Column(Text, nullable=True)
    course_id         = Column(CHAR(36), ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    created_by        = Column(CHAR(36), ForeignKey("users.id",   ondelete="CASCADE"),  nullable=False)
    time_limit_mins   = Column(Integer, nullable=False, default=60)
    shuffle_questions = Column(Boolean, default=False)
    shuffle_options   = Column(Boolean, default=False)
    status            = Column(Enum(QuizStatus), default=QuizStatus.draft)
    pass_score        = Column(Float, default=50.0)
    max_attempts      = Column(Integer, default=1)
    available_from    = Column(DateTime, nullable=True)
    available_until   = Column(DateTime, nullable=True)
    total_marks       = Column(Float, default=0.0)
    created_at        = Column(DateTime, default=datetime.utcnow)
    updated_at        = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course          = relationship("Course",      back_populates="quizzes")
    created_by_user = relationship("User",        back_populates="quizzes")
    questions       = relationship("Question",    back_populates="quiz",
                                   order_by="Question.order_index",
                                   cascade="all, delete-orphan")
    attempts        = relationship("QuizAttempt", back_populates="quiz")

    __table_args__ = (
        Index("idx_quizzes_course",  "course_id"),
        Index("idx_quizzes_status",  "status"),
        Index("idx_quizzes_created", "created_by"),
    )


# ─── QUESTION ────────────────────────────────────────────────

class Question(Base):
    __tablename__ = "questions"

    id          = Column(CHAR(36), primary_key=True, default=gen_uuid)
    quiz_id     = Column(CHAR(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    content     = Column(Text,    nullable=False)
    type        = Column(Enum(QuestionType), nullable=False, default=QuestionType.single_choice)
    marks       = Column(Float,   nullable=False, default=1.0)
    explanation = Column(Text,    nullable=True)
    order_index = Column(Integer, default=0)
    image_url   = Column(Text,    nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    quiz    = relationship("Quiz", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question",
                           order_by="QuestionOption.order_index",
                           cascade="all, delete-orphan")

    __table_args__ = (Index("idx_questions_quiz", "quiz_id"),)


# ─── QUESTION OPTION ─────────────────────────────────────────

class QuestionOption(Base):
    __tablename__ = "question_options"

    id          = Column(CHAR(36), primary_key=True, default=gen_uuid)
    question_id = Column(CHAR(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    content     = Column(Text,    nullable=False)
    is_correct  = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    image_url   = Column(Text,    nullable=True)

    question = relationship("Question", back_populates="options")

    __table_args__ = (Index("idx_options_question", "question_id"),)


# ─── QUIZ ATTEMPT ────────────────────────────────────────────

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id              = Column(CHAR(36), primary_key=True, default=gen_uuid)
    quiz_id         = Column(CHAR(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    student_id      = Column(CHAR(36), ForeignKey("users.id",   ondelete="CASCADE"), nullable=False)
    status          = Column(Enum(AttemptStatus), default=AttemptStatus.in_progress)
    started_at      = Column(DateTime, default=datetime.utcnow)
    submitted_at    = Column(DateTime, nullable=True)
    time_spent_secs = Column(Integer,  nullable=True)
    score           = Column(Float,    nullable=True)
    total_marks     = Column(Float,    nullable=True)
    percentage      = Column(Float,    nullable=True)
    passed          = Column(Boolean,  nullable=True)
    question_order  = Column(JSON,     nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    quiz    = relationship("Quiz",          back_populates="attempts")
    student = relationship("User",          back_populates="attempts")
    answers = relationship("AttemptAnswer", back_populates="attempt",
                           cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_attempts_quiz",    "quiz_id"),
        Index("idx_attempts_student", "student_id"),
        Index("idx_attempts_status",  "status"),
    )


# ─── ATTEMPT ANSWER ──────────────────────────────────────────

class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"

    id               = Column(CHAR(36), primary_key=True, default=gen_uuid)
    attempt_id       = Column(CHAR(36), ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id      = Column(CHAR(36), ForeignKey("questions.id",     ondelete="CASCADE"), nullable=False)
    selected_options = Column(JSON, nullable=True)
    text_answer      = Column(Text, nullable=True)
    is_correct       = Column(Boolean, nullable=True)
    marks_awarded    = Column(Float,   nullable=True)
    answered_at      = Column(DateTime, default=datetime.utcnow)

    attempt  = relationship("QuizAttempt", back_populates="answers")
    question = relationship("Question")

    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id"),
        Index("idx_answers_attempt", "attempt_id"),
    )
