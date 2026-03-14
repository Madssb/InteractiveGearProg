# syntax=docker/dockerfile:1
FROM python:3.12-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.10.2 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_DEV=1

WORKDIR /app/backend

COPY backend/pyproject.toml backend/uv.lock ./
COPY osrswiki_images /app/osrswiki_images

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

COPY backend /app/backend

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
