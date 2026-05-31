#!/usr/bin/env bash
set -euo pipefail

PASS=0
FAIL=0
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

pass() { echo "PASSED: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAILED: $1"; FAIL=$((FAIL + 1)); }

echo "=== Release Readiness Verification ==="
echo ""

echo "--- Phase 38 Docs ---"
for doc in \
  "docs/releases/PHASE37_RELEASE_READINESS.md" \
  "docs/runbooks/ROLLBACK_RUNBOOK.md" \
  "docs/reports/PHASE_TRACEABILITY_MATRIX.md" \
  "docs/runbooks/GO_LIVE_CHECKLIST.md"; do
  if [[ -f "$doc" ]]; then
    pass "Phase 38 doc exists: $doc"
  else
    fail "Phase 38 doc missing: $doc"
  fi
done

echo ""
echo "--- Phase 39 Docs ---"
for doc in \
  "docs/runbooks/PRODUCTION_DRY_RUN_VERIFICATION.md" \
  "docs/reports/PHASE39_PRODUCTION_DRY_RUN_REPORT.md"; do
  if [[ -f "$doc" ]]; then
    pass "Phase 39 doc exists: $doc"
  else
    fail "Phase 39 doc missing: $doc"
  fi
done

echo ""
echo "--- Phase 40 Docs ---"
for doc in \
  "docs/runbooks/GO_LIVE_REHEARSAL.md" \
  "docs/reports/PHASE40_GO_LIVE_REHEARSAL_REPORT.md"; do
  if [[ -f "$doc" ]]; then
    pass "Phase 40 doc exists: $doc"
  else
    fail "Phase 40 doc missing: $doc"
  fi
done

echo ""
echo "--- Phase 39 Scripts ---"
for script in \
  "scripts/prod/verify-prod-runtime.sh" \
  "scripts/prod/verify-prod-health.sh" \
  "scripts/prod/verify-prod-rollback-readiness.sh" \
  "scripts/prod/verify-prod-observability.sh"; do
  if [[ -x "$script" ]]; then
    pass "Phase 39 script executable: $script"
  else
    fail "Phase 39 script missing or not executable: $script"
  fi
done

echo ""
echo "--- Phase 40 Scripts ---"
for script in \
  "scripts/prod/verify-go-live-safety-locks.sh" \
  "scripts/prod/capture-go-live-evidence.sh" \
  "scripts/prod/run-go-live-rehearsal.sh"; do
  if [[ -x "$script" ]]; then
    pass "Phase 40 script executable: $script"
  else
    fail "Phase 40 script missing or not executable: $script"
  fi
done

echo ""
echo "--- Release Decision ---"
RELEASE_DOC="docs/releases/PHASE37_RELEASE_READINESS.md"
if [[ -f "$RELEASE_DOC" ]]; then
  if grep -q "Status:.*GO" "$RELEASE_DOC" 2>/dev/null; then
    pass "Release decision is GO"
  else
    fail "Release decision is not GO in $RELEASE_DOC"
  fi
else
  fail "Release readiness doc not found at $RELEASE_DOC"
fi

echo ""
echo "--- Safety Locks Documented ---"
ENV_EXAMPLE=".env.example"
if [[ -f "$ENV_EXAMPLE" ]]; then
  for key in DRY_RUN LIVE_TRADING_ACK MT5_ENABLED PRODUCTION_ALLOW_LIVE_ACTIONS RISK_GUARDIAN_ENABLED; do
    if grep -Eq "^\s*${key}\s*=" "$ENV_EXAMPLE" 2>/dev/null; then
      pass "Safety lock $key is documented in $ENV_EXAMPLE"
    else
      fail "Safety lock $key not found in $ENV_EXAMPLE"
    fi
  done
else
  fail ".env.example not found"
fi

echo ""
echo "--- Rollback Runbook ---"
ROLLBACK_DOC="docs/runbooks/ROLLBACK_RUNBOOK.md"
if [[ -f "$ROLLBACK_DOC" ]]; then
  pass "Rollback runbook exists at $ROLLBACK_DOC"
else
  fail "Rollback runbook not found at $ROLLBACK_DOC"
fi

echo ""
echo "--- Go-Live Rehearsal Runbook ---"
REHEARSAL_DOC="docs/runbooks/GO_LIVE_REHEARSAL.md"
if [[ -f "$REHEARSAL_DOC" ]]; then
  pass "Go-live rehearsal runbook exists at $REHEARSAL_DOC"
else
  fail "Go-live rehearsal runbook not found at $REHEARSAL_DOC"
fi

echo ""
echo "--- No .env Files Tracked ---"
TRACKED_ENV=$(git ls-files '*.env*' 2>/dev/null | grep -v '.env.example' | grep -v '.gitignore' || true)
if [[ -z "$TRACKED_ENV" ]]; then
  pass "No .env files tracked by git"
else
  fail "Tracked .env files found: $TRACKED_ENV"
fi

echo ""
echo "--- No Secret Values Tracked ---"
if grep -rnE '(API_KEY|SECRET|PASSWORD|TOKEN)=[a-zA-Z0-9_]{16,}' --include='*.py' --include='*.ts' --include='*.tsx' --include='*.sh' --include='*.yml' --include='*.yaml' --include='*.json' . 2>/dev/null | grep -v '.env.example' | grep -v '__pycache__' | grep -v 'node_modules' | grep -v '.git/' | grep -qvE '(placeholder|your-|changeme|example|test-token|test-key)'; then
  fail "Potential secret values found in tracked files"
else
  pass "No secret-looking values tracked"
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS, Failed: $FAIL"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
