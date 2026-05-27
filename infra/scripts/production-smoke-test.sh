#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost}"
MAX_RETRIES="${MAX_RETRIES:-30}"
SLEEP_SECONDS="${SLEEP_SECONDS:-2}"

wait_for_http() {
  local url="$1"
  local retries="$2"
  local sleep_seconds="$3"

  local attempt=1
  until curl -fsS "${url}" >/dev/null; do
    if [ "${attempt}" -ge "${retries}" ]; then
      echo "Service did not become ready at ${url}" >&2
      return 1
    fi
    attempt="$((attempt + 1))"
    sleep "${sleep_seconds}"
  done
}

wait_for_http "${BASE_URL}/" "${MAX_RETRIES}" "${SLEEP_SECONDS}"
wait_for_http "${BASE_URL}/api/health" "${MAX_RETRIES}" "${SLEEP_SECONDS}"

METRICS_STATUS="$(curl -sS -o /dev/null -w "%{http_code}" "${BASE_URL}/api/metrics")"
if [ "${METRICS_STATUS}" != "200" ] && [ "${METRICS_STATUS}" != "401" ] && [ "${METRICS_STATUS}" != "403" ]; then
  echo "Unexpected /api/metrics HTTP status: ${METRICS_STATUS}" >&2
  exit 1
fi

echo "Production smoke test passed for ${BASE_URL}"
