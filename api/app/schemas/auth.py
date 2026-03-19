from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "student"

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    faculty_id: Optional[str] = None
    avatar: Optional[str] = None
    language: Optional[str] = "vi"
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user: UserOut


class LogoutResponse(BaseModel):
    success: bool = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    language: Optional[str] = None
