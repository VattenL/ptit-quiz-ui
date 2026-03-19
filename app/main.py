from fastapi import FastAPI
from app.routers import quiz, result

app = FastAPI(title="Quiz API", version="1.0.0")

app.include_router(quiz.router)
app.include_router(result.router)


@app.get("/")
def root():
    return {"status": "running", "docs": "/docs"}
