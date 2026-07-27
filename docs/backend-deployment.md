# Backend setup

This document describes implementation details for making the repo backend endpoints available. Requires bootstrapped PostgreSQL database and tables. (See [PostgreSQL](postgresql-bootstrapping.md)).

## uv

This section describes using `uv` to make the repo backend api endpoints available on `127.0.01:8000`:

```bash
cd backend
uv sync
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

- Requires [uv](https://docs.astral.sh/uv/getting-started/installation/)
- port 8000 availability on localhost

## Docker

This section describes building and running a docker image to make the repo backend api endpoints available on `127.0.0.1:8000`:

```bash
# build image manually
docker build -t ladlorapi-backend -f backend/Dockerfile .

# run container manually
docker run -d \
  --name ladlor-test \
  -p 8000:8000 \
  --env-file .env \
  ladlorapi-backend

# verify
docker ps # test container
curl http://localhost:8000/health # test endpoint availability with healthcheck

# cleanup
docker stop ladlor-test
docker rm ladlor-test
```

- Requires [Docker](https://docs.docker.com/engine/install/).
- port 8000 availability on localhost

## Docker Compose

This section describes using Docker Compose to make the repo backend api endpoitns available at `VITE_API_BASE_URL`

```bash
docker compose up -d
```

Requires the following:

- Docker compose
- `cloudflared` bootstrapped (see [cloudflared](cloudflared-bootstrapping.md))

## Systemd

TBA
