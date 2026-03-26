from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AttemptOut(BaseModel):
    id           : str
    quiz_id      : str
    student_id   : str
    score        : Optional[float] = None
    total_marks  : Optional[float] = None
    percentage   : Optional[float] = None
    passed       : Optional[bool] = None
    created_at   : Optional[datetime] = None

    model_config = {"from_attributes": True}


class ResultsResponse(BaseModel):
    average_score : float
    pass_rate     : float
    attempts      : List[AttemptOut]


class StudentResultItem(BaseModel):
    quiz_id      : str
    title        : str
    score        : Optional[float] = None
    passed       : Optional[bool] = None
    created_at   : Optional[datetime] = None

    model_config = {"from_attributes": True}


class StudentResultsResponse(BaseModel):
    results : List[StudentResultItem]
