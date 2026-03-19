from datetime import datetime, timezone
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="student", index=True)
    class_name: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = Field(default=None)


class RevokedToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    token_jti: str = Field(index=True, unique=True)
    revoked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
