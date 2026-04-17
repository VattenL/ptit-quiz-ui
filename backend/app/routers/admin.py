from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.schemas import AuthResponse, LoginRequest, UserPublic
from app.security import create_access_token, verify_password
from app.routers.deps import to_user_public, get_current_admin

router = APIRouter(tags=["admin"])

@router.post("/api/admin/login", response_model=AuthResponse)
def admin_login(payload: LoginRequest, response: Response, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.username == payload.username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
    
    if user.role.lower().strip() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin")
    
    access_token = create_access_token(user.username)
    
    # Cũng thiết lập cookie cho admin
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=86400, samesite="lax")
    response.set_cookie(key="language", value="vi", max_age=86400)
    response.set_cookie(key="theme", value="light", max_age=86400)
    response.set_cookie(key="profile_visits", value="0", max_age=86400)
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=to_user_public(user),
    )
    
@router.get("/api/get/students", response_model=list[UserPublic])
def get_all_students(admin: User = Depends(get_current_admin), db: Session = Depends(get_session)):
    users = db.exec(select(User).where(User.role.lower().strip() == "student")).all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    return [to_user_public(user) for user in users]
