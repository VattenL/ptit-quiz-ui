from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.deps import get_current_user
from app.models.models import User, TokenBlacklist
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, LogoutResponse, UserOut

router = APIRouter(prefix="/auth", tags=["Auth"])
bearer = HTTPBearer()


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email, User.is_active == True).first()
    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(token=token, user=UserOut.model_validate(user))


@router.post("/logout", response_model=LogoutResponse)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    try:
        payload = decode_token(token)
        exp = payload.get("exp")
        expires_at = datetime.utcfromtimestamp(exp) if exp else datetime.utcnow() + timedelta(days=7)
    except Exception:
        expires_at = datetime.utcnow() + timedelta(days=7)
    db.add(TokenBlacklist(token=token, user_id=current_user.id, expires_at=expires_at))
    db.commit()
    return LogoutResponse()
