from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ─── Option ───────────────────────────────

class OptionCreate(BaseModel):
    content: str
    is_correct: bool = False
    order_index: int = 0
    image_url: Optional[str] = None


class OptionOut(BaseModel):
    id: str
    content: str
    is_correct: bool
    order_index: int
    image_url: Optional[str] = None
    model_config = {"from_attributes": True}


class OptionPublic(BaseModel):
    id: str
    content: str
    order_index: int
    image_url: Optional[str] = None
    model_config = {"from_attributes": True}


# ─── Question ─────────────────────────────

class QuestionCreate(BaseModel):
    content: str
    type: str = "single_choice"
    marks: float = 1.0
    explanation: Optional[str] = None
    order_index: int = 0
    image_url: Optional[str] = None
    options: List[OptionCreate] = []


class QuestionUpdate(BaseModel):
    content: Optional[str] = None
    type: Optional[str] = None
    marks: Optional[float] = None
    explanation: Optional[str] = None
    order_index: Optional[int] = None
    image_url: Optional[str] = None
    options: Optional[List[OptionCreate]] = None


class QuestionOut(BaseModel):
    id: str
    content: str
    type: str
    marks: float
    explanation: Optional[str] = None
    order_index: int
    image_url: Optional[str] = None
    options: List[OptionOut] = []
    model_config = {"from_attributes": True}


# ─── Quiz ─────────────────────────────────

class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: Optional[str] = None
    time_limit_mins: int = 60
    shuffle_questions: bool = False
    shuffle_options: bool = False
    pass_score: float = 50.0
    max_attempts: int = 1
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    course_id: Optional[str] = None
    time_limit_mins: Optional[int] = None
    shuffle_questions: Optional[bool] = None
    shuffle_options: Optional[bool] = None
    status: Optional[str] = None
    pass_score: Optional[float] = None
    max_attempts: Optional[int] = None
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None


class QuizSummary(BaseModel):
    quiz_id: str
    title: str
    description: Optional[str] = None
    course_id: Optional[str] = None
    status: str
    time_limit_mins: int
    total_marks: float
    created_at: datetime


class QuizDetail(BaseModel):
    quiz_id: str
    title: str
    description: Optional[str] = None
    course_id: Optional[str] = None
    status: str
    time_limit_mins: int
    shuffle_questions: bool
    shuffle_options: bool
    pass_score: float
    max_attempts: int
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    total_marks: float
    questions: List[QuestionOut] = []
    created_at: datetime


class QuizListResponse(BaseModel):
    quizzes: List[QuizSummary]
    total: int
    page: int
    limit: int


class QuizCreateResponse(BaseModel):
    quiz_id: str
    created_at: datetime


class SortItem(BaseModel):
    question_id: str
    index: int


class SortRequest(BaseModel):
    order: List[SortItem]


# ─── Attempt ──────────────────────────────

class AnswerSubmit(BaseModel):
    question_id: str
    selected_options: Optional[List[str]] = None
    text_answer: Optional[str] = None


class AttemptSubmit(BaseModel):
    answers: List[AnswerSubmit]


class AttemptOut(BaseModel):
    id: str
    quiz_id: str
    student_id: str
    status: str
    started_at: datetime
    submitted_at: Optional[datetime] = None
    time_spent_secs: Optional[int] = None
    score: Optional[float] = None
    total_marks: Optional[float] = None
    percentage: Optional[float] = None
    passed: Optional[bool] = None
    model_config = {"from_attributes": True}


# ─── Results ──────────────────────────────

class StudentResult(BaseModel):
    quiz_id: str
    title: str
    score: Optional[float]
    total_marks: Optional[float]
    percentage: Optional[float]
    passed: Optional[bool]
    attempted_at: datetime


class StudentResultsResponse(BaseModel):
    results: List[StudentResult]
