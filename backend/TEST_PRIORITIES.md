# Backend Test Matrix

Purpose: current snapshot of backend test coverage and remaining high-value gaps.

## Current Coverage

### Fast, deterministic suite (default)

Covered by:

- `backend/tests/test_api_guardrails.py`
- `backend/tests/test_api_routes.py`

What is verified:

- client identity extraction (`CF-Connecting-IP` preference)
- trusted host rejection (`400`)
- request size rejection (`413`) and invalid `Content-Length` rejection (`400`)
- rate-limit core behavior (`429` + `Retry-After`)
- health endpoint contract (`{"status":"ok"}`)
- metadata route response shape (mocked resolver)
- share create/load behavior (mocked DB layer)

Run:

```bash
cd backend
uv run pytest -q
```

### DB integration checks (`@pytest.mark.db`)

Covered by:

- `backend/tests/test_db_integration.py`

What is verified:

- database connectivity (`SELECT 1`)
- schema contract for `public.shares`:
  - required columns (`token`, `milestone_sequence`)
  - primary key on `token`

Run:

```bash
cd backend
uv run pytest -m db -q
```

### Live HTTP checks (`@pytest.mark.live`)

Covered by:

- `backend/tests/test_live_api.py`

What is verified:

- `GET /share` unknown token -> `404`
- `GET /share` known token -> `200`
- `POST /fetch-milestone-metadata` smoke response shape
- `POST /share` roundtrip + cleanup
- rate-limit route behavior returns `429` + `Retry-After`
- invalid `Host` header rejection (`400`)
- oversized body rejection (`413`)

Run:

```bash
cd backend
RUN_LIVE_TESTS=1 LIVE_API_BASE_URL=http://127.0.0.1:8000 uv run pytest -m live -q
```

For mutating share live test:

```bash
cd backend
RUN_LIVE_TESTS=1 LIVE_API_BASE_URL=http://127.0.0.1:8000 uv run pytest -m live -q
```

Run mutating live tests only against a backend started with `DATABASE_URL`
pointing at a dedicated test database.

## Remaining Optional Gaps

These are not blockers for current self-hosted production, but are good next improvements:

1. Body-size boundary acceptance test

- explicit test for request size exactly at max limit.

2. Fresh-schema DB roundtrip

- disposable DB test that applies `schema.sql`, then runs `save_share` + `load_share`.

3. Logging assertions

- automated check that request and rate-limit logs include expected fields.

## Practical Release Gate

For backend changes before deploy:

1. `uv run pytest -q`
2. `uv run pytest -m db -q` (with real DB env)
3. `RUN_LIVE_TESTS=1 ... uv run pytest -m live -q` (against running service)

If all three pass, backend is considered release-ready for current scope.
