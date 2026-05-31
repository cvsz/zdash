#!/usr/bin/env bash
set -euo pipefail

ZDASH_RUNTIME="${ZDASH_PROD_RUNTIME:-/opt/zdash/runtime}"
PASS=0
FAIL=0

pass() { echo "PASSED: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAILED: $1"; FAIL=$((FAIL + 1)); }

echo "=== Production Health Verification ==="
echo ""

if [[ ! -d "$ZDASH_RUNTIME" ]]; then
  echo "FAILED: Production runtime not found at $ZDASH_RUNTIME"
  echo "Run: sudo ./install-zdash-prod.sh"
  exit 1
fi

BACKEND_PORT="${BACKEND_PORT:-8005}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

echo "--- Backend Health ---"
HEALTH_URL="http://localhost:${BACKEND_PORT}/health"
if HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$HEALTH_URL" 2>/dev/null); then
  if [[ "$HTTP_CODE" == "200" ]]; then
    pass "Backend health endpoint responds HTTP 200 at $HEALTH_URL"
  else
    fail "Backend health endpoint at $HEALTH_URL returned HTTP $HTTP_CODE"
  fi
else
  fail "Backend health endpoint at $HEALTH_URL unreachable"
fi

echo ""
echo "--- Backend Safety Check ---"
SAFETY_URL="http://localhost:${BACKEND_PORT}/api/admin/safety-check"
if HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$SAFETY_URL" 2>/dev/null); then
  if [[ "$HTTP_CODE" == "200" ]]; then
    pass "Backend safety check passes at $SAFETY_URL"
  else
    fail "Backend safety check at $SAFETY_URL returned HTTP $HTTP_CODE"
  fi
else
  fail "Backend safety check at $SAFETY_URL unreachable"
fi

echo ""
echo "--- Frontend Health ---"
FRONTEND_URL="http://localhost:${FRONTEND_PORT}"
if HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$FRONTEND_URL" 2>/dev/null); then
  if [[ "$HTTP_CODE" == "200" ]]; then
    pass "Frontend responds HTTP 200 at $FRONTEND_URL"
  else
    fail "Frontend at $FRONTEND_URL returned HTTP $HTTP_CODE"
  fi
else
  fail "Frontend at $FRONTEND_URL unreachable"
fi

echo ""
echo "--- Risk System ---"
RISK_URL="http://localhost:${BACKEND_PORT}/api/risk/status"
if BODY=$(curl -s --max-time 5 "$RISK_URL" 2>/dev/null); then
  if echo "$BODY" | grep -q '"halted"'; then
    pass "Risk system responds at $RISK_URL"
  else
    fail "Risk system response missing expected fields"
  fi
else
  fail "Risk system at $RISK_URL unreachable"
fi

echo ""
echo "--- Port Exposure ---"
if ss -tlnp 2>/dev/null | grep -q ":${BACKEND_PORT} "; then
  pass "Backend port ${BACKEND_PORT} is listening"
else
  fail "Backend port ${BACKEND_PORT} not listening"
fi

if ss -tlnp 2>/dev/null | grep -q ":${FRONTEND_PORT} "; then
  pass "Frontend port ${FRONTEND_PORT} is listening"
else
  fail "Frontend port ${FRONTEND_PORT} not listening"
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS, Failed: $FAIL"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
