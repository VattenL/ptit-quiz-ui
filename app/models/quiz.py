from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base


class Faculty(Base):
    __tablename__ = "faculties"

    id         = Column(String(36), primary_key=True)
    name       = Column(String(255))
    code       = Column(String(50))
    created_at = Column(DateTime)

    users   = relationship("User", back_populates="faculty")
    courses = relationship("Course", back_populates="faculty")


class User(Base):
    __tablename__ = "users"

    id             = Column(String(36), primary_key=True)
    name           = Column(String(255))
    email          = Column(String(255))
    password_hash  = Column(Text)
    role           = Column(Enum("student", "teacher", "admin"))
    faculty_id     = Column(String(36), ForeignKey("faculties.id"))
    avatar         = Column(Text)
    language       = Column(String(10))
    oauth_provider = Column(String(50))
    oauth_id       = Column(String(255))
    is_active      = Column(Boolean)
    created_at     = Column(DateTime)
    updated_at     = Column(DateTime)

    faculty  = relationship("Faculty", back_populates="users")
    quizzes  = relationship("Quiz", back_populates="creator")
    attempts = relationship("QuizAttempt", back_populates="student")


class Course(Base):
    __tablename__ = "courses"

    id          = Column(String(36), primary_key=True)
    name        = Column(String(255))
    code        = Column(String(50))
    description = Column(Text)
    faculty_id  = Column(String(36), ForeignKey("faculties.id"))
    teacher_id  = Column(String(36), ForeignKey("users.id"))
    is_active   = Column(Boolean)
    created_at  = Column(DateTime)
    updated_at  = Column(DateTime)

    faculty = relationship("Faculty", back_populates="courses")
    quizzes = relationship("Quiz", back_populates="course")


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    id          = Column(String(36), primary_key=True)
    course_id   = Column(String(36), ForeignKey("courses.id"))
    student_id  = Column(String(36), ForeignKey("users.id"))
    enrolled_at = Column(DateTime)


class Quiz(Base):
    __tablename__ = "quizzes"

    id                = Column(String(36), primary_key=True)
    title             = Column(String(255))
    description       = Column(Text)
    course_id         = Column(String(36), ForeignKey("courses.id"))
    created_by        = Column(String(36), ForeignKey("users.id"))
    time_limit_mins   = Column(Integer)
    shuffle_questions = Column(Boolean)
    shuffle_options   = Column(Boolean)
    status            = Column(Enum("draft", "published"))
    pass_score        = Column(Float)
    max_attempts      = Column(Integer)
    available_from    = Column(DateTime)
    available_until   = Column(DateTime)
    total_marks       = Column(Float)
    order             = Column(Integer, default=0)
    created_at        = Column(DateTime)
    updated_at        = Column(DateTime)

    course    = relationship("Course", back_populates="quizzes")
    creator   = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", order_by="Question.order_index")
    attempts  = relationship("QuizAttempt", back_populates="quiz")


class Question(Base):
    __tablename__ = "questions"

    id          = Column(String(36), primary_key=True)
    quiz_id     = Column(String(36), ForeignKey("quizzes.id"))
    content     = Column(Text)
    type        = Column(Enum("multiple_choice", "true_false", "short_answer"))
    marks       = Column(Float)
    explanation = Column(Text)
    order_index = Column(Integer)
    image_url   = Column(Text)
    created_at  = Column(DateTime)
    updated_at  = Column(DateTime)

    quiz    = relationship("Quiz", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", order_by="QuestionOption.order_index")


class QuestionOption(Base):
    __tablename__ = "question_options"

    id          = Column(String(36), primary_key=True)
    question_id = Column(String(36), ForeignKey("questions.id"))
    content     = Column(Text)
    is_correct  = Column(Boolean)
    order_index = Column(Integer)
    image_url   = Column(Text)

    question = relationship("Question", back_populates="options")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id              = Column(String(36), primary_key=True)
    quiz_id         = Column(String(36), ForeignKey("quizzes.id"))
    student_id      = Column(String(36), ForeignKey("users.id"))
    status          = Column(Enum("in_progress", "submitted", "graded"))
    started_at      = Column(DateTime)
    submitted_at    = Column(DateTime)
    time_spent_secs = Column(Integer)
    score           = Column(Float)
    total_marks     = Column(Float)
    percentage      = Column(Float)
    passed          = Column(Boolean)
    question_order  = Column(JSON)
    created_at      = Column(DateTime)

    quiz    = relationship("Quiz", back_populates="attempts")
    student = relationship("User", back_populates="attempts")


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"

    id               = Column(String(36), primary_key=True)
    attempt_id       = Column(String(36), ForeignKey("quiz_attempts.id"))
    question_id      = Column(String(36), ForeignKey("questions.id"))
    selected_options = Column(JSON)
    text_answer      = Column(Text)
    is_correct       = Column(Boolean)
    marks_awarded    = Column(Float)
    answered_at      = Column(DateTime)


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id         = Column(String(36), primary_key=True)
    token      = Column(Text)
    user_id    = Column(String(36), ForeignKey("users.id"))
    expires_at = Column(DateTime)
    created_at = Column(DateTime)
