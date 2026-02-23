# Backend Setup

## Requirements

- Python 3.12.x
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

From `backend/`:

```bash
uv sync
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

For laptop self-hosting behind Cloudflare Tunnel, keep API bound to `127.0.0.1` and route external traffic through `cloudflared`.

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

## API Endpoints

- `POST /sequence/`
- `POST /share/`
- `GET /share/?token=...`
- `GET /health`

## Testing

From `backend/`:

```bash
uv sync
uv run pytest
```

## Rate Limiting

The backend enforces per-client limits on:

- `POST /sequence/`
- `POST /share/`

Policy:

- max 3 requests per second
- max 20 requests per minute

Client identity is read from `CF-Connecting-IP` (fallback: `X-Forwarded-For`, then socket IP).
When exceeded, API returns `429 Too Many Requests` with a `Retry-After` response header.

## Guardrails

- Trusted host check allows only:
  - `api.ladlorchart.com`
  - `localhost`
  - `127.0.0.1`
- Request size limit: max 256 KiB body (`413` on exceed).
- Request logging records method/path/status/latency/client/host.
