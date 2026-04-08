# Backend setup

This document describes implementation details for the InteractiveGearProg backend.

Note that the implementations each insist on a unique port for avoiding port conflicts.

## Requirements

- Python 3.12.x
- PostgreSQL
- uv (recommended)
- env file in `backend/` like that of `.env.example`

## Locally hosted implementation with uv (quickstart)

This section describes using `uv` to run the backend locally.

Deployment with uv is simple and fast. However, exposing the backend requires separate systemd services (e.g. for tunneling). A notable benefit is rapid iteration during development.

- Requires [uv](https://docs.astral.sh/uv/getting-started/installation/)
- port 8000 availability on localhost

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
- port 8001 availability on localhost

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

This section describes deploying the backend and tunneling it with Docker Compose.

Requires the following:

- Docker compose
- `cloudflared` is bootstrapped (see `cloudflared-bootstrapping.md`)

Two explicit Compose files are provided so prod and test tunnel selection is always intentional.

`compose.test.yaml` exists primarily to validate the Docker Compose deployment path end-to-end without disrupting the live service. It is a proving ground and fallback path, not a requirement for long-term concurrent operation with prod.

`compose.prod.yaml` is the intended steady-state Compose deployment once that path is trusted.

### Test tunnel

From `backend/` run:

```bash
docker compose -f compose.test.yaml up -d --build
```

This publishes the backend on `localhost:8003` for direct debugging and routes tunnel traffic through `infra/cloudflared/config.test.yml`.

### Prod tunnel

From `backend/` run:

```bash
docker compose -f compose.prod.yaml up -d --build
```

This publishes the backend on `localhost:8002` for direct debugging and routes tunnel traffic through `infra/cloudflared/config.prod.yml`.

## system service implementation

Requires the following:

- Docker compose
- project in `/opt` with appropriate privilidges (`sudo chown -R $USER:$USER /opt/InteractiveGearProg`)

Bootstrapping:

- `git pull`
- `sudo cp /opt/InteractiveGearProg/infra/systemd/* /etc/systemd & systemctl daemon-reload`

start: `sudo systemctl start ladlor.target`
stop: `sudo systemctl start ladlor.target`
restart: `sudo systemctl restart ladlor.target`
