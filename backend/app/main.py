from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="PTIT Exam Backend", version="0.1.0")


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/login")
def login(_: LoginRequest) -> dict[str, str]:
    # TODO: Replace with real authentication logic and JWT issuing.
    raise HTTPException(status_code=501, detail="Login is not implemented yet")
