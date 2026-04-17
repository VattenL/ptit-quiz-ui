from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlmodel import Session, select

from app.database import get_session
from app.models import User, RevokedToken
from app.schemas import AuthResponse, LoginRequest, RegisterRequest, MessageResponse, UserPublic
from app.security import create_access_token, hash_password, verify_password, extract_jti
from app.routers.deps import to_user_public, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.username == payload.username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    
    access_token = create_access_token(user.username)
    
    # Thiết lập cookie cho JWT và các preferences
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=86400, samesite="lax")
    response.set_cookie(key="language", value="vi", max_age=86400) # Mặc định là Tiếng Việt
    response.set_cookie(key="theme", value="light", max_age=86400) # Mặc định không dark mode
    response.set_cookie(key="profile_visits", value="0", max_age=86400) # Khởi tạo biến đếm
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=to_user_public(user),
    )
    
@router.post("/register", response_model=UserPublic)
def register(payload: RegisterRequest, db: Session = Depends(get_session)):
    username = db.exec(select(User).where(User.username == payload.username)).first()
    if username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username taken")
    
    email = db.exec(select(User).where(User.email == payload.email)).first()
    if email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email taken")
    
    if len(payload.password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password too short")
    
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password does not match")
    
    user = User(
        full_name=payload.fullname.strip(),
        username=payload.username.strip(),
        email=payload.email.strip(),
        password_hash=hash_password(payload.password),
        role="student",
        class_name=None,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return to_user_public(user)

@router.post("/logout", response_model=MessageResponse)
def logout(
    request: Request, 
    response: Response,
    db: Session = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    # Lấy token từ header hoặc cookie để thu hồi
    token = request.cookies.get("access_token")
    if not token and request.headers.get("Authorization"):
        token = request.headers.get("Authorization").split(" ")[1]
        
    if token:
        jti = extract_jti(token)
        revoked_token = RevokedToken(token_jti=jti)
        db.add(revoked_token)
        db.commit()
        
    # Xoá cookie
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="profile_visits")
    
    return MessageResponse(detail="Logged out successfully.")
