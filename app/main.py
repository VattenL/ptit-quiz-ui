from fastapi import FastAPI
from routers import quiz, result
from core.database import engine
from models.quiz import Base
from seed import create_seed_data

# Create SQLite database and tables if they don't exist
Base.metadata.create_all(bind=engine)

# Seed the database with mock data if it is empty
create_seed_data()

app = FastAPI(title="Quiz API", version="1.0.0")

app.include_router(quiz.router)
app.include_router(result.router)


@app.get("/")
def root():
    return {"status": "running", "docs": "/docs"}
