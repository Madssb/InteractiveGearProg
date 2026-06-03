# Backend Testing

Placeholder documentation dump for testing-related docs. cleanup later.

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

For live tests that create shares, start the backend with `DATABASE_URL` pointed at a
dedicated test database.

```bash
RUN_LIVE_TESTS=1 LIVE_API_BASE_URL=http://127.0.0.1:8000 uv run pytest -m live
```