#!/usr/bin/env bash
set -euo pipefail

PASS=0
FAIL=0

pass() { echo "PASSED: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAILED: $1"; FAIL=$((FAIL + 1)); }

echo "=== Production Observability Verification ==="
echo ""

ZDASH_RUNTIME="${ZDASH_PROD_RUNTIME:-/opt/zdash/runtime}"
if [[ ! -d "$ZDASH_RUNTIME" ]]; then
  echo "FAILED: Production runtime not found at $ZDASH_RUNTIME"
  echo "Run: sudo ./install-zdash-prod.sh"
  exit 1
fi

echo "--- Realtime Endpoints ---"
REALTIME_DOC="docs/runbooks/REALTIME_GATEWAY.md"
if [[ -f "$REALTIME_DOC" ]]; then
  if grep -q "WebSocket\|channel\|/api/realtime/ws" "$REALTIME_DOC" 2>/dev/null; then
    pass "Realtime endpoints documented in $REALTIME_DOC"
  else
    fail "Realtime doc exists but missing endpoint documentation"
  fi
else
  fail "Realtime gateway documentation not found at $REALTIME_DOC"
fi

echo ""
echo "--- Observability Runbooks ---"
declare -A OBS_DOCS=(
  ["OBSERVABILITY"]="docs/runbooks/OBSERVABILITY.md"
  ["INCIDENT_RESPONSE"]="docs/runbooks/INCIDENT_RESPONSE.md"
  ["KILL_SWITCH"]="docs/runbooks/KILL_SWITCH.md"
  ["RISK_HALT"]="docs/runbooks/RISK_HALT_RUNBOOK.md"
  ["BACKUP_RESTORE"]="docs/runbooks/BACKUP_RESTORE.md"
  ["DEPLOYMENT"]="docs/runbooks/DEPLOYMENT_RUNBOOK.md"
  ["DB_MIGRATION"]="docs/runbooks/DB_MIGRATION.md"
)

for name in "${!OBS_DOCS[@]}"; do
  doc="${OBS_DOCS[$name]}"
  if [[ -f "$doc" ]]; then
    pass "Observability runbook $name exists at $doc"
  else
    fail "Observability runbook $name not found at $doc"
  fi
done

echo ""
echo "--- Docker Compose Config ---"
COMPOSE_FILE="${ZDASH_PROD_COMPOSE:-$ZDASH_RUNTIME/docker-compose.yml}"
if [[ -f "$COMPOSE_FILE" ]]; then
  if docker compose -f "$COMPOSE_FILE" config >/dev/null 2>&1; then
    pass "Docker Compose config is valid at $COMPOSE_FILE"
  else
    fail "Docker Compose config is invalid at $COMPOSE_FILE"
  fi
else
  echo "  (skipping compose validation — no production compose file at $COMPOSE_FILE)"
fi

echo ""
echo "--- Local Docker Compose Config ---"
for compose_file in docker-compose.yml docker-compose.prod.yml; do
  if [[ -f "$compose_file" ]]; then
    if docker compose -f "$compose_file" config >/dev/null 2>&1; then
      pass "Docker Compose config is valid at $compose_file"
    else
      fail "Docker Compose config is invalid at $compose_file"
    fi
  fi
done

echo ""
echo "--- Logs Verification ---"
LOGS_SCRIPT="${ZDASH_PROD_LOGS:-$ZDASH_RUNTIME/scripts/zdash-logs.sh}"
if [[ -f "$LOGS_SCRIPT" ]]; then
  if [[ -x "$LOGS_SCRIPT" ]]; then
    pass "Logs helper is executable at $LOGS_SCRIPT"
  else
    fail "Logs helper is not executable at $LOGS_SCRIPT"
  fi
else
  echo "  (skipping logs check — no production logs helper)"
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS, Failed: $FAIL"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
