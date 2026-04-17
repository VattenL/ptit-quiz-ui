from fastapi import Depends, HTTPException, status, Header, Request
from jose import ExpiredSignatureError, JWTError
from sqlmodel import Session, select

from app.database import get_session
from app.models import User, RevokedToken
from app.schemas import UserPublic
from app.security import extract_jti, decode_access_token

def to_user_public(user: User) -> UserPublic:
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID is missing after persistence",
        )

    return UserPublic(
        id=user.id,
        fullname=user.full_name,
        username=user.username,
        email=user.email,
        role=user.role,
        class_name=user.class_name,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
    )

def get_current_user(
    request: Request,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_session)
) -> User:
    # Ưu tiên lấy token từ cookie trước, nếu không có mới lấy từ header (phòng trường hợp tool cũ gọi api)
    token = request.cookies.get("access_token")
    if not token:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = authorization.split(" ")[1]
    
    try:
        payload = decode_access_token(token)
        username: str | None = payload.get("sub")
        jti: str | None = payload.get("jti")
        if username is None or jti is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    is_revoked = db.exec(select(RevokedToken).where(RevokedToken.token_jti == jti)).first()
    if is_revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked. Please log in again.")
    
    user = db.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

def get_current_admin(user: User = Depends(get_current_user)):
    if user.role.lower().strip() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return user
