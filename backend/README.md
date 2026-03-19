# FastAPI Backend

This backend now includes SQLModel database support and authentication routes for register, login, logout, and current user lookup.

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Open API docs:

- http://localhost:8000/docs
- http://localhost:8000/redoc

## Implemented authentication APIs

- `POST /api/auth/register`
	- Body: `fullname`, `username`, `email`, `password`, `confirm_password` (optional)
	- Creates a user in SQLite via SQLModel and returns public user data
- `POST /api/auth/login`
	- Body: `username`, `password`
	- Returns a bearer JWT and user data
- `POST /api/auth/logout`
	- Body: `access_token`
	- Revokes token by storing token JTI in database
- `GET /api/auth/me`
	- Header: `Authorization: Bearer <token>`
	- Returns current authenticated user

## Database

- Engine: SQLite
- Path: `backend/data/ptit_exam.db`
- Tables:
	- `user`
	- `revokedtoken`

Tables are auto-created on startup.
