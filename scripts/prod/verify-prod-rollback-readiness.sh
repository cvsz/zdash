#!/usr/bin/env bash
set -euo pipefail

PASS=0
FAIL=0

pass() { echo "PASSED: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAILED: $1"; FAIL=$((FAIL + 1)); }

echo "=== Production Rollback Readiness Verification ==="
echo ""

ZDASH_RUNTIME="${ZDASH_PROD_RUNTIME:-/opt/zdash/runtime}"
if [[ ! -d "$ZDASH_RUNTIME" ]]; then
  echo "FAILED: Production runtime not found at $ZDASH_RUNTIME"
  echo "Run: sudo ./install-zdash-prod.sh"
  exit 1
fi

echo "--- Safety Environment Values ---"
ENV_FILE="${ZDASH_PROD_ENV:-$ZDASH_RUNTIME/.env.production}"
if [[ ! -f "$ENV_FILE" ]]; then
  fail ".env.production not found at $ENV_FILE"
else
  echo "  (checking safety flags without printing secrets)"
  check_env() {
    local key="$1"
    local expected="$2"
    if grep -Eq "^\s*${key}\s*=\s*${expected}\s*" "$ENV_FILE" 2>/dev/null; then
      pass "${key}=${expected}"
    else
      fail "${key} is not set to ${expected} in $ENV_FILE"
    fi
  }
  check_env "DRY_RUN" "true"
  check_env "LIVE_TRADING_ACK" "false"
  check_env "MT5_ENABLED" "false"
  check_env "PRODUCTION_ALLOW_LIVE_ACTIONS" "false"
  check_env "RISK_GUARDIAN_ENABLED" "true"
fi

echo ""
echo "--- Backend Port ---"
ENV_BACKEND_PORT="$(grep -s '^BACKEND_PORT=' "$ENV_FILE" 2>/dev/null | head -1 | cut -d= -f2 | tr -d '[:space:]')"
if [[ -z "$ENV_BACKEND_PORT" ]]; then
  echo "  BACKEND_PORT not set in env, using default 8005"
  ENV_BACKEND_PORT="8005"
fi
if [[ "$ENV_BACKEND_PORT" == "8005" ]]; then
  pass "Backend port is ${ENV_BACKEND_PORT}"
else
  fail "Backend port is ${ENV_BACKEND_PORT}, expected 8005"
fi

echo ""
echo "--- Rollback Documentation ---"
ROLLBACK_DOCS=(
  "docs/runbooks/ROLLBACK_RUNBOOK.md"
  "docs/runbooks/rollback-runbook.md"
  "docs/runbooks/ROLLBACK.md"
)
for doc in "${ROLLBACK_DOCS[@]}"; do
  if [[ -f "$doc" ]]; then
    pass "Rollback documentation exists at $doc"
    break
  fi
done

echo ""
echo "--- Release Readiness Documentation ---"
RELEASE_DOC="docs/releases/PHASE37_RELEASE_READINESS.md"
if [[ -f "$RELEASE_DOC" ]]; then
  if grep -q "Status:.*GO" "$RELEASE_DOC" 2>/dev/null; then
    pass "Release readiness report exists and status is GO"
  else
    fail "Release readiness report exists but status is not GO"
  fi
else
  fail "Release readiness report not found at $RELEASE_DOC"
fi

echo ""
echo "--- Go-Live Checklist ---"
GO_LIVE_DOC="docs/runbooks/GO_LIVE_CHECKLIST.md"
if [[ -f "$GO_LIVE_DOC" ]]; then
  pass "Go-live checklist exists at $GO_LIVE_DOC"
else
  fail "Go-live checklist not found at $GO_LIVE_DOC"
fi

echo ""
echo "--- Production Dry-Run Verification Doc ---"
DRY_RUN_DOC="docs/runbooks/PRODUCTION_DRY_RUN_VERIFICATION.md"
if [[ -f "$DRY_RUN_DOC" ]]; then
  pass "Production dry-run verification doc exists at $DRY_RUN_DOC"
else
  fail "Production dry-run verification doc not found at $DRY_RUN_DOC"
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS, Failed: $FAIL"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
