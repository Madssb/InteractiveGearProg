# Backend

This directory contains the FastAPI backend that powers ladlorchart.com. This README is the quickest path for getting the service running locally and points to the deeper docs when you need deployment or runtime details.

## Requirements

- Python 3.12.x
- PostgreSQL database (Neon or local)
- uv (recommended)
- env file in `backend/` like that of `.env.example`

## Quick start

```bash
uv sync
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

## Environment

Ensure an `.env` file exists in `backend/`. The backend reads it at startup for database configuration and related runtime settings.

## Database Schema

Apply schema from `backend/schema.sql`:

```bash
psql "$DATABASE_URL" -f backend/schema.sql
```

This creates `public.shares` used by `/share/` endpoints.

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

## Testing

From `backend/`:

```bash
uv sync
uv run pytest
```

DB connectivity smoke check (requires real `DATABASE_URL`):

```bash
uv run pytest -m db
```

Live API checks (requires running backend server):

```bash
RUN_LIVE_TESTS=1 LIVE_API_BASE_URL=http://127.0.0.1:8000 uv run pytest -m live
```

Live mutating share test safely against test table:

```bash
RUN_LIVE_TESTS=1 SHARES_TABLE=shares_test LIVE_API_BASE_URL=http://127.0.0.1:8000 uv run pytest -m live
```

Current test coverage and remaining optional gaps are tracked in:

- `backend/TEST_PRIORITIES.md`

## Related Docs

- [docs/backend-reference.md](/home/mads/InteractiveGearProg/docs/backend-reference.md)
- [docs/backend-deployment.md](/home/mads/InteractiveGearProg/docs/backend-deployment.md)
- [docs/cloudflared-bootstrapping.md](/home/mads/InteractiveGearProg/docs/cloudflared-bootstrapping.md)
