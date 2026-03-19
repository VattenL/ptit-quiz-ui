# FastAPI Backend Scaffold

This folder is a starter backend scaffold for replacing former client-side auth logic.

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

## Next steps

- Implement `/api/auth/login` with password hashing and JWT.
- Add registration endpoint and database persistence.
- Connect frontend forms to this API.
