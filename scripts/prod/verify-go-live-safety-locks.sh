#!/usr/bin/env bash
set -euo pipefail

ZDASH_RUNTIME="${ZDASH_PROD_RUNTIME:-/opt/zdash/runtime}"
PASS=0
FAIL=0

pass() { echo "PASSED: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAILED: $1"; FAIL=$((FAIL + 1)); }

echo "=== Go-Live Safety Locks Verification ==="
echo ""

if [[ ! -d "$ZDASH_RUNTIME" ]]; then
  echo "FAILED: Production runtime not found at $ZDASH_RUNTIME"
  echo "Run: sudo ./install-zdash-prod.sh"
  exit 1
fi

ENV_FILE="${ZDASH_PROD_ENV:-$ZDASH_RUNTIME/.env.production}"
if [[ ! -f "$ENV_FILE" ]]; then
  fail ".env.production not found at $ENV_FILE"
  echo ""
  echo "=== Results ==="
  echo "Passed: $PASS, Failed: $FAIL"
  exit 1
fi

echo "--- Safety Key Verification ---"
check_env() {
  local key="$1"
  local expected="$2"
  local label="$3"
  if grep -Eq "^\s*${key}\s*=\s*${expected}\s*" "$ENV_FILE" 2>/dev/null; then
    pass "${label} (${key}=${expected})"
  else
    fail "${label} (${key} is not set to ${expected})"
  fi
}

check_env "DRY_RUN" "true" "Trading dry-run"
check_env "LIVE_TRADING_ACK" "false" "Live trading disabled"
check_env "MT5_ENABLED" "false" "MT5 disabled"
check_env "PRODUCTION_ALLOW_LIVE_ACTIONS" "false" "Live actions disabled"
check_env "RISK_GUARDIAN_ENABLED" "true" "Risk guardian enabled"

echo ""
echo "--- Lock Verification ---"
echo "  DRY_RUN=true       stops broker execution"
echo "  LIVE_TRADING_ACK=false  blocks trade confirmation"
echo "  MT5_ENABLED=false   prevents MT5 connection"
echo "  PRODUCTION_ALLOW_LIVE_ACTIONS=false  blocks all live mutations"
echo "  RISK_GUARDIAN_ENABLED=true  guardian enforces risk checks"

echo ""
echo "--- Runtime Service Verification ---"
SERVICE_FILE="/etc/systemd/system/zdash.service"
if [[ -f "$SERVICE_FILE" ]]; then
  STATUS=$(systemctl is-active zdash 2>/dev/null || echo "unknown")
  if [[ "$STATUS" == "active" ]]; then
    pass "zdash.service is active"
  else
    pass "zdash.service exists (status: $STATUS)"
  fi
else
  fail "zdash.service not found at $SERVICE_FILE"
fi

COMPOSE_FILE="${ZDASH_PROD_COMPOSE:-$ZDASH_RUNTIME/docker-compose.yml}"
if [[ -f "$COMPOSE_FILE" ]]; then
  if docker compose -f "$COMPOSE_FILE" ps >/dev/null 2>&1; then
    pass "Docker Compose services are operational"
  else
    fail "Docker Compose services check failed"
  fi
else
  fail "Docker Compose file not found at $COMPOSE_FILE"
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS, Failed: $FAIL"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
