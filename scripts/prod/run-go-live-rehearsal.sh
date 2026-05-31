#!/usr/bin/env bash
set -euo pipefail

ZDASH_RUNTIME="${ZDASH_PROD_RUNTIME:-/opt/zdash/runtime}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0
START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

pass() { echo "PASSED: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAILED: $1"; FAIL=$((FAIL + 1)); }

echo "============================================"
echo "  zDash Go-Live Rehearsal"
echo "  Started: $START_TIME"
echo "============================================"
echo ""

if [[ ! -d "$ZDASH_RUNTIME" ]]; then
  echo "FAILED: Production runtime not found at $ZDASH_RUNTIME"
  echo "Run: sudo ./install-zdash-prod.sh"
  exit 1
fi

echo "============================================"
echo "  Phase 1: Production Runtime Verification"
echo "============================================"
if bash "$SCRIPT_DIR/verify-prod-runtime.sh"; then
  pass "Runtime verification"
else
  fail "Runtime verification"
fi
echo ""

echo "============================================"
echo "  Phase 2: Health Verification"
echo "============================================"
if bash "$SCRIPT_DIR/verify-prod-health.sh"; then
  pass "Health verification"
else
  fail "Health verification"
fi
echo ""

echo "============================================"
echo "  Phase 3: Safety Locks Verification"
echo "============================================"
if bash "$SCRIPT_DIR/verify-go-live-safety-locks.sh"; then
  pass "Safety locks verification"
else
  fail "Safety locks verification"
fi
echo ""

echo "============================================"
echo "  Phase 4: Rollback Readiness"
echo "============================================"
if bash "$SCRIPT_DIR/verify-prod-rollback-readiness.sh"; then
  pass "Rollback readiness"
else
  fail "Rollback readiness"
fi
echo ""

echo "============================================"
echo "  Phase 5: Observability Verification"
echo "============================================"
if bash "$SCRIPT_DIR/verify-prod-observability.sh"; then
  pass "Observability verification"
else
  fail "Observability verification"
fi
echo ""

echo "============================================"
echo "  Phase 6: Evidence Capture"
echo "============================================"
if bash "$SCRIPT_DIR/capture-go-live-evidence.sh"; then
  pass "Evidence capture"
else
  fail "Evidence capture"
fi
echo ""

END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "============================================"
echo "  Go-Live Rehearsal Complete"
echo "  Started:  $START_TIME"
echo "  Finished: $END_TIME"
echo "  Passed: $PASS, Failed: $FAIL"
echo "============================================"

if [[ "$FAIL" -gt 0 ]]; then
  echo ""
  echo "WARNING: $FAIL check(s) failed. Review output above before proceeding to go-live."
  echo "See: docs/runbooks/GO_LIVE_REHEARSAL.md"
  exit 1
fi

echo ""
echo "All checks passed. System is ready for go-live."
echo "See: docs/runbooks/GO_LIVE_CHECKLIST.md"
