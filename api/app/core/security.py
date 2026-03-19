from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    # bcrypt giới hạn 72 bytes — encode + truncate
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    pwd_bytes = plain.encode("utf-8")[:72]
    return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
