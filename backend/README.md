# Backend Setup

## Requirements

- Python 3.11+
- PostgreSQL database (Neon or local)

## Environment

Set `DATABASE_URL` before starting the API.

Example:

```bash
export DATABASE_URL="postgresql://user:password@host:5432/dbname?sslmode=require"
```

`backend/db.py` reads this value at startup.

## Database Schema

Apply schema from `backend/schema.sql`:

```bash
psql "$DATABASE_URL" -f backend/schema.sql
```

This creates `public.shares` used by `/share/` endpoints.

## Run Locally

From repo root:

```bash
python3 -m pip install -r backend/requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

## API Endpoints

- `POST /sequence/`
- `POST /share/`
- `GET /share/?token=...`
- `GET /health`
