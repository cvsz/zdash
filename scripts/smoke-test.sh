#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"

echo "== /health =="
curl -sS "$BASE_URL/health" | jq . || curl -sS "$BASE_URL/health"

echo "== /api/agents =="
curl -sS "$BASE_URL/api/agents" | jq . || curl -sS "$BASE_URL/api/agents"

echo "== /api/logs =="
curl -sS "$BASE_URL/api/logs" | jq . || curl -sS "$BASE_URL/api/logs"

echo "== /api/agents/message =="
curl -sS -X POST "$BASE_URL/api/agents/message" \
  -H "Content-Type: application/json" \
  -d '{"from_agent":"ceo","to_agent":"janie","message":"Hello Janie, report status.","context":{}}' \
  | jq . || true
