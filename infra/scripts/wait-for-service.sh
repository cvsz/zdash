#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-}"
PORT="${2:-}"
TIMEOUT_SECONDS="${3:-60}"

if [ -z "${HOST}" ] || [ -z "${PORT}" ]; then
  echo "Usage: $0 <host> <port> [timeout-seconds]" >&2
  exit 1
fi

START="$(date +%s)"

while true; do
  if (echo > "/dev/tcp/${HOST}/${PORT}") >/dev/null 2>&1; then
    echo "Service reachable at ${HOST}:${PORT}"
    exit 0
  fi

  NOW="$(date +%s)"
  ELAPSED="$((NOW - START))"
  if [ "${ELAPSED}" -ge "${TIMEOUT_SECONDS}" ]; then
    echo "Timed out waiting for ${HOST}:${PORT} after ${TIMEOUT_SECONDS}s" >&2
    exit 1
  fi

  sleep 1
done
