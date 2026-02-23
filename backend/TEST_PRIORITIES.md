# Backend Test Priorities

Purpose: prioritize test coverage for local self-hosting rollout with focus on stability and safety.

## Current Baseline

Already covered in `backend/tests/test_api_guardrails.py`:

- client identity extraction (`CF-Connecting-IP` preference)
- trusted host rejection (`400`)
- request size limit behavior (`413` and invalid `Content-Length` -> `400`)
- rate-limit core behavior (`429` + `Retry-After`)

## Priority 0 (Before Exposure)

Goal: confirm core API behavior works on real requests, not just unit-level guards.

1. Health endpoint integration test
- `GET /health` returns `200` and `{"status":"ok"}`.

2. Sequence endpoint integration test (mock wiki)
- `POST /sequence/` with valid payload returns `200` and expected response shape.
- Mock `search_many` to avoid external network dependency in test.

3. Share endpoint integration test (mock DB layer)
- `POST /share/` returns token.
- `GET /share/?token=...` returns stored payload shape.
- Patch `save_share` / `load_share` in app module to avoid real DB in this stage.

Done criteria:
- All Priority 0 tests green in CI/local with one command: `uv run pytest`.

## Priority 1 (Operational Safety)

Goal: verify hardening behavior under realistic request patterns.

1. Rate-limit route behavior
- Repeated `POST /sequence/` hits `429` on threshold.
- Confirm `Retry-After` header exists and is parseable.

2. Trusted host allowlist behavior
- allowed host succeeds (`api.ladlorchart.com`, localhost).
- non-allowlisted host rejected.

3. Body-size limit behavior
- boundary case at limit accepted.
- over-limit rejected with `413`.

Done criteria:
- No regressions in guardrails after backend changes.

## Priority 2 (Data/DB Reliability)

Goal: prevent schema/runtime drift and DB contract breakage.

1. DB contract test (integration; optional separate marker)
- against a disposable Postgres instance:
  - apply `backend/schema.sql`
  - verify `save_share` inserts
  - verify `load_share` retrieves expected JSON payload

2. Schema smoke validation
- Ensure `shares` table has required columns (`token`, `sequence`, `items`) and primary key.

Done criteria:
- DB layer validated on fresh schema from version-controlled SQL.

## Priority 3 (Self-Hosting Ops Validation)

Goal: confidence in laptop-hosted deployment path.

1. Startup sanity
- missing `DATABASE_URL` fails fast with clear message.
- valid `DATABASE_URL` starts successfully.

2. Tunnel-adjacent behavior
- host header and client IP extraction still correct behind proxy headers.

3. Logging sanity
- request logs include method/path/status/latency/client/host.
- rate-limit violations generate warning logs.

Done criteria:
- runbook steps in `backend/README.md` are validated in practice.

## Suggested Test Structure (Incremental)

Keep current layout (no `src/` refactor required):

- `backend/tests/test_api_guardrails.py` (existing)
- `backend/tests/test_api_routes.py` (new, mocked integration)
- `backend/tests/test_db_integration.py` (new, optional marker `@pytest.mark.db`)

## Execution Commands

From `backend/`:

```bash
uv sync
uv run pytest
```

Optional DB test group (when created):

```bash
uv run pytest -m db
```

## Notes for Tomorrow

- Start with `test_api_routes.py` first (highest value per effort).
- Keep external dependencies mocked by default (wiki/DB) so tests stay fast and deterministic.
- Add DB integration tests after route tests are stable.
