# Backend Setup

## Requirements

- Python 3.12.x
- PostgreSQL database (Neon or local)

## Environment

Set `DATABASE_URL` before starting the API.
Optional: set `SHARES_TABLE` (defaults to `shares`).

Example:

```bash
export DATABASE_URL="postgresql://user:password@host:5432/dbname?sslmode=require"
export SHARES_TABLE="shares"
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

## Cloudflare Tunnel

Recommended run order:

1. Start backend locally.
2. Start `cloudflared` tunnel.
3. Verify `/health` through the public hostname.

Quick temporary tunnel (testing only):

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

Named tunnel (stable path):

```bash
cloudflared tunnel login
cloudflared tunnel create ladlorchart-api
cloudflared tunnel route dns ladlorchart-api api.ladlorchart.com
```

Default config file location:

- `/home/mads/.cloudflared/config.yml`

Example `~/.cloudflared/config.yml`:

```yaml
tunnel: <TUNNEL_ID>
credentials-file: /home/mads/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: api.ladlorchart.com
    service: http://127.0.0.1:8000
  - service: http_status:404
```

Run named tunnel:

```bash
cloudflared tunnel run ladlorchart-api
```

If config is not in the default location:

```bash
cloudflared --config /path/to/config.yml tunnel run ladlorchart-api
```

## Systemd Operations

Service templates are versioned in:

- `backend/backend.service`
- `backend/tunnel.service`
- `backend/heartbeat.service`
- `backend/heartbeat.timer`

Install as user services:

```bash
mkdir -p ~/.config/systemd/user
cp backend/backend.service ~/.config/systemd/user/
cp backend/tunnel.service ~/.config/systemd/user/
cp backend/heartbeat.service ~/.config/systemd/user/
cp backend/heartbeat.timer ~/.config/systemd/user/
systemctl --user daemon-reload
```

Create heartbeat env file (replace URL with your provider URL):

```bash
mkdir -p ~/.config
cat > ~/.config/heartbeat.env << 'EOF'
HEARTBEAT_URL=https://example-healthcheck-url
# Optional:
# HEARTBEAT_TIMEOUT_SECONDS=10
EOF
chmod 600 ~/.config/heartbeat.env
```

Enable and start:

```bash
systemctl --user enable --now backend.service
systemctl --user enable --now tunnel.service
systemctl --user enable --now heartbeat.timer
```

Routine operations:

```bash
systemctl --user status backend.service tunnel.service heartbeat.timer
systemctl --user restart backend.service tunnel.service heartbeat.timer
journalctl --user -u backend.service -u tunnel.service -u heartbeat.service -f
```

List timer schedule:

```bash
systemctl --user list-timers heartbeat.timer
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

### Interpreting pytest output

- `skipped`: test was selected, but runtime conditions were not met (for example missing env flag/DB URL).
- `deselected`: test was excluded by your selection filter (for example `-m live` only runs live-marked tests).

Examples:

- `uv run pytest -q` -> broad/default run (you may see some `skipped`).
- `uv run pytest -m live -q` -> live-only run (non-live tests show as `deselected`).

Current test coverage and remaining optional gaps are tracked in:

- `backend/TEST_PRIORITIES.md`

## Rollback

Current deployment path is self-hosted backend + Cloudflare Tunnel.

Fast rollback steps:

1. Revert backend code/config to last known-good state.
2. Restart services:
```bash
systemctl --user restart backend.service tunnel.service
```
3. Verify health:
```bash
curl -si https://api.ladlorchart.com/health | sed -n '1,20p'
```

If a future alternate origin exists, DNS rollback can also be used by repointing `api.ladlorchart.com` to that fallback target.

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
