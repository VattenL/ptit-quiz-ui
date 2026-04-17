from typing import Annotated

from fastapi import FastAPI
try:
    from .database import create_db_and_tables
    from .routers import auth, users, admin
except ImportError:
    from database import create_db_and_tables
    from routers import auth, users, admin

app = FastAPI(title="PTIT Exam Backend", version="0.1.0")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)

@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()

@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

    
    return to_user_public(current_user)