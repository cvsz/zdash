#!/usr/bin/env bash
set -euo pipefail

ZDASH_RUNTIME="${ZDASH_PROD_RUNTIME:-/opt/zdash/runtime}"
PASS=0
FAIL=0

pass() { echo "PASSED: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAILED: $1"; FAIL=$((FAIL + 1)); }

echo "=== Production Runtime Verification ==="
echo "Runtime path: $ZDASH_RUNTIME"
echo ""

if [[ ! -d "$ZDASH_RUNTIME" ]]; then
  echo "FAILED: Production runtime not found at $ZDASH_RUNTIME"
  echo "Run: sudo ./install-zdash-prod.sh"
  exit 1
fi
pass "Runtime directory exists at $ZDASH_RUNTIME"

SERVICE_FILE="/etc/systemd/system/zdash.service"
if [[ -f "$SERVICE_FILE" ]]; then
  pass "zdash.service exists"
else
  fail "zdash.service not found at $SERVICE_FILE"
fi

COMPOSE_FILE="${ZDASH_PROD_COMPOSE:-$ZDASH_RUNTIME/docker-compose.yml}"
if [[ -f "$COMPOSE_FILE" ]]; then
  pass "Docker Compose file exists at $COMPOSE_FILE"
else
  fail "Docker Compose file not found at $COMPOSE_FILE"
fi

ENV_FILE="${ZDASH_PROD_ENV:-$ZDASH_RUNTIME/.env.production}"
if [[ -f "$ENV_FILE" ]]; then
  pass ".env.production exists at $ENV_FILE (not printing secrets)"
else
  fail ".env.production not found at $ENV_FILE"
fi

HEALTH_SCRIPT="${ZDASH_PROD_HEALTH:-$ZDASH_RUNTIME/scripts/zdash-health.sh}"
if [[ -f "$HEALTH_SCRIPT" ]]; then
  pass "Health helper exists at $HEALTH_SCRIPT"
else
  fail "Health helper not found at $HEALTH_SCRIPT"
fi

LOGS_SCRIPT="${ZDASH_PROD_LOGS:-$ZDASH_RUNTIME/scripts/zdash-logs.sh}"
if [[ -f "$LOGS_SCRIPT" ]]; then
  pass "Logs helper exists at $LOGS_SCRIPT"
else
  fail "Logs helper not found at $LOGS_SCRIPT"
fi

BACKUP_SCRIPT="${ZDASH_PROD_BACKUP:-$ZDASH_RUNTIME/scripts/zdash-backup.sh}"
if [[ -f "$BACKUP_SCRIPT" ]]; then
  pass "Backup helper exists at $BACKUP_SCRIPT"
else
  fail "Backup helper not found at $BACKUP_SCRIPT"
fi

UPDATE_SCRIPT="${ZDASH_PROD_UPDATE:-$ZDASH_RUNTIME/scripts/zdash-update.sh}"
if [[ -f "$UPDATE_SCRIPT" ]]; then
  pass "Update helper exists at $UPDATE_SCRIPT"
else
  fail "Update helper not found at $UPDATE_SCRIPT"
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS, Failed: $FAIL"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
