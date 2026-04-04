# Backend setup

This document describes implementation details for the InteractiveGearProg backend.

## Requirements

- Python 3.12.x
- PostgreSQL
- uv (recommended)
- env file in `backend/` like that of `.env.example`

## Locally hosted implementation with uv (quickstart)

This section describes using `uv` to run the backend locally.

Deployment with uv is simple and fast. However, exposing the backend requires separate systemd services (e.g. for tunneling). A notable benefit is rapid iteration during development.

- Requires [uv](https://docs.astral.sh/uv/getting-started/installation/)

From `backend/` run the following:

```bash
# run with uv
uv sync
uv run uvicorn main:app --host 127.0.0.1 --port 8000

# verify (optional)
uv run pytest
```

can be terminated with ctrl + c if in the foreground, and `kill <pid>`if in the background. `ps aux | grep 8000` identifies the pid.

## Locally hosted implementation with docker

This section describes deploying the InteractiveGearProg backend locally with a docker container.

Running the backend as a standalone Docker container (without Docker Compose) is primarily useful for debugging and verification. It is more complex than with uv with more steps for implementation, and more difficult bootstrapping.

- Requires [Docker](https://docs.docker.com/engine/install/).

From project root run the following:

```bash
# build image manually
docker build -t ladlorapi-backend -f backend/Dockerfile .

# run container manually
docker run -d \
  --name ladlor-test \
  -p 8001:8000 \
  --env-file backend/.env \
  ladlorapi-backend

# verify
docker ps # test container
curl http://localhost:8001/health # test endpoint availability with healthcheck

# cleanup
docker stop ladlor-test
docker rm ladlor-test
```

## Localhost to prod

This section describes tunneling the locally hosted backend to `api.ladlorchart.com` with the `cloudflared` daemon.

docker compose for unified deployment of the backend and tunneling is preferred, but fallback could be required, and thus we explain the alternative.

Requirements:

- backend is hosted on `127.0.0.1:8000`
- `cloudflared` is bootstrapped (see `cloudfared-bootstrapping.md`)

From project root run the following:

```bash
cloudflared tunnel --config infra/cloudflared/config.local.yml run
```

## Orchestration with Docker Compose

This section describes deploying the backend and tunneling it with docker compose.

Requires the following:

- Docker compose
- `cloudflared` is bootstrapped (see `cloudfared-bootstrapping.md`)

From `backend` rund the following:

```bash
  docker compose -f compose.yaml up -d
```
