#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8005}"

curl -fsS "$BASE_URL/api/scheduler/status"
curl -fsS "$BASE_URL/api/scheduler/jobs"

create_payload='{"name":"Smoke Health Check","job_type":"health_check","schedule_type":"manual","payload":{},"enabled":true}'
created_json="$(curl -fsS -X POST "$BASE_URL/api/scheduler/jobs" -H 'Content-Type: application/json' -d "$create_payload")"
job_id="$(printf '%s' "$created_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['job']['id'])")"

curl -fsS -X POST "$BASE_URL/api/scheduler/jobs/$job_id/run"
