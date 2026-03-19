from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, Header, Request
from jose import ExpiredSignatureError, JWTError
from sqlmodel import Session, select

try:
    from .database import create_db_and_tables, get_session
    from .models import User, RevokedToken
    from .schemas import AuthResponse, LoginRequest, RegisterRequest, UserPublic, MessageResponse, LogoutRequest, UserUpdateRequest
    from .security import create_access_token, hash_password, verify_password, extract_jti, decode_access_token
except ImportError:
    from database import create_db_and_tables, get_session
    from models import User, RevokedToken
    from schemas import AuthResponse, LoginRequest, RegisterRequest, UserPublic, MessageResponse, LogoutRequest, UserUpdateRequest
    from security import create_access_token, hash_password, verify_password, extract_jti, decode_access_token

app = FastAPI(title="PTIT Exam Backend", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


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

@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.username == payload.username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    
    access_token = create_access_token(user.username)
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=to_user_public(user),
    )
    
@app.post("/api/auth/register", response_model=UserPublic)
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

def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_session)) -> User:
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

@app.post("/api/auth/logout", response_model=MessageResponse)
def logout(authorization: str = Header(default=None), db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    token = authorization.split(" ")[1]
    jti = extract_jti(token)
    revoked_token = RevokedToken(token_jti=jti)
    db.add(revoked_token)
    db.commit()
    db.refresh(revoked_token)
    
    return MessageResponse(detail="Logged out successfully.")

@app.get("/api/users/me", response_model=UserPublic)
def get_me(current_user: User = Depends(get_current_user)):
    return to_user_public(current_user)

@app.post("/api/admin/login", response_model=AuthResponse)
def admin_login(payload: LoginRequest, db: Session = Depends(get_session)):
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
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=to_user_public(user),
    )
    
@app.get("/api/get/students", response_model=list[UserPublic])
def get_all_students(admin: User = Depends(get_current_admin), db: Session = Depends(get_session)):
    users = db.exec(select(User).where(User.role.lower().strip() == "student")).all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    return [to_user_public(user) for user in users]

@app.put("/api/update/user", response_model=UserPublic)
def update_user(payload: UserUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return to_user_public(current_user)