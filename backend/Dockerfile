# syntax=docker/dockerfile:1
# check=error=true

# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# Install the project into `/app`
WORKDIR /app

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Required by backend.main and backend.milestones.
COPY data/logic/*.json /app/data/logic/

# Required by backend.annotations
COPY data/contents/changelog.json /app/data/contents/changelog.json

# Required by backend.discord_bot.
COPY data/generated/milestone-metadata.json /app/data/generated/milestone-metadata.json

# Required by shared.id_asset.
COPY data/cache/names.json /app/data/cache/names.json

# Required by shared.manual_asset.
COPY frontend/public/images/prayer_icons /app/frontend/public/images/prayer_icons
COPY frontend/public/images/skill_icons /app/frontend/public/images/skill_icons
COPY frontend/public/images/spell_icons /app/frontend/public/images/spell_icons
COPY frontend/public/images/slayer_icons /app/frontend/public/images/slayer_icons

# Required actual code
COPY backend /app/backend
COPY shared /app/shared

# data/chartbuilder-assets is expected to be a shared volume.

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --project backend

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Use the non-root user to run our application
USER nonroot

# Image found everything it needed if this passes.
RUN uv run --project backend python -m backend.tests.test_required_files_exist

CMD ["uv", "run", "--project", "backend",  "--no-sync", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
