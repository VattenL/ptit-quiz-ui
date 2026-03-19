from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.api.routes import auth, users, courses, quizzes, attempts, results

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{(time.time() - start) * 1000:.2f}ms"
    return response

API = "/api/v1"
app.include_router(auth.router,     prefix=API)
app.include_router(users.router,    prefix=API)
app.include_router(courses.router,  prefix=API)
app.include_router(quizzes.router,  prefix=API)
app.include_router(attempts.router, prefix=API)
app.include_router(results.router,  prefix=API)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": settings.APP_VERSION}

@app.get("/", tags=["Health"])
def root():
    return {"message": f"Welcome to {settings.APP_NAME}", "docs": "/docs"}
