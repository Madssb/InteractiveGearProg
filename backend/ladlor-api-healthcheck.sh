#!/usr/bin/env bash
set -euo pipefail

: "${HEARTBEAT_URL:?HEARTBEAT_URL is not set in EnvironmentFile}"

curl \
  --fail \
  --silent \
  --show-error \
  --max-time "${HEARTBEAT_TIMEOUT_SECONDS:-10}" \
  "${HEARTBEAT_URL}" \
  > /dev/null
