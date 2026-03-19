from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel


class RegisterRequest(SQLModel):
    fullname: str
    username: str
    email: EmailStr
    password: str
    confirm_password: str


class LoginRequest(SQLModel):
    username: str
    password: str


class LogoutRequest(SQLModel):
    access_token: str


class UserPublic(SQLModel):
    id: int
    fullname: str
    username: str
    email: EmailStr
    role: str
    class_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


class AuthResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class MessageResponse(SQLModel):
    detail: str
