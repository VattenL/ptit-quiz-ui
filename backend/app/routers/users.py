from fastapi import APIRouter, Depends, Request, Response
from sqlmodel import Session

from app.database import get_session
from app.models import User
from app.schemas import UserPublic, UserUpdateRequest
from app.routers.deps import to_user_public, get_current_user

router = APIRouter(tags=["users"])

@router.get("/api/users/me", response_model=UserPublic)
def get_me(
    response: Response, 
    request: Request, 
    current_user: User = Depends(get_current_user)
):
    # Đọc counter profile_visits từ Cookie đã set lúc login
    visits_str = request.cookies.get("profile_visits", "0")
    try:
        visits = int(visits_str)
    except ValueError:
        visits = 0
    
    # Tăng biến đếm và lưu lại Cookie mới
    visits += 1
    response.set_cookie(key="profile_visits", value=str(visits), max_age=86400)
    
    return to_user_public(current_user)

@router.put("/api/update/user", response_model=UserPublic)
def update_user(
    payload: UserUpdateRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_session)
):
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return to_user_public(current_user)
