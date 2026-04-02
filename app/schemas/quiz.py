from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Enum

class QuizListItem(BaseModel):
    id              : str
    title           : str
    description     : Optional[str] = None
    course_id       : Optional[str] = None
    status          : Optional[str] = None
    time_limit_mins : Optional[int] = None
    total_marks     : Optional[float] = None
    created_at      : Optional[datetime] = None

    model_config = {"from_attributes": True}


class QuizListResponse(BaseModel):
    quizzes : List[QuizListItem]
    total   : int
    page    : int


class QuizCreateInput(BaseModel):
    title             : str
    description       : Optional[str] = None
    course_id         : str
    time_limit_mins   : Optional[int] = None
    shuffle_questions : bool = False
    shuffle_options   : bool = False
    status            : Optional[str] = "draft"
    pass_score        : Optional[float] = None
    max_attempts      : Optional[int] = None


class QuizCreateResponse(BaseModel):
    quiz_id    : str
    created_at : Optional[datetime] = None


class QuizUpdateInput(BaseModel):
    title             : Optional[str] = None
    description       : Optional[str] = None
    time_limit_mins   : Optional[int] = None
    shuffle_questions : Optional[bool] = None
    shuffle_options   : Optional[bool] = None
    status            : Optional[str] = None
    pass_score        : Optional[float] = None
    max_attempts      : Optional[int] = None


class OptionOut(BaseModel):
    id          : str
    content     : Optional[str] = None
    is_correct  : Optional[bool] = None
    order_index : Optional[int] = None

    model_config = {"from_attributes": True}


class QuestionOut(BaseModel):
    id          : str
    content     : Optional[str] = None
    type        : Optional[str] = None
    marks       : Optional[float] = None
    order_index : Optional[int] = None
    options     : List[OptionOut] = []

    model_config = {"from_attributes": True}


class QuizDetailResponse(BaseModel):
    quiz_id         : str
    title           : str
    time_limit_mins : Optional[int] = None
    total_marks     : Optional[float] = None
    questions       : List[QuestionOut] = []

    model_config = {"from_attributes": True}


class SortInput(BaseModel):
    quiz_ids : List[str]


class SuccessResponse(BaseModel):
    success : bool = True
