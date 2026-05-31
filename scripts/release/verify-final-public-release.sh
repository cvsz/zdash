#!/usr/bin/env bash
set -euo pipefail

PASS=0
FAIL=0

pass() { echo "PASSED: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAILED: $1"; FAIL=$((FAIL + 1)); }

echo "=== Final Public Release Verification ==="
echo ""

echo "--- Required Files ---"
for f in \
  "README.md" \
  "CHANGELOG.md" \
  "VERSION" \
  "docs/releases/FINAL_RELEASE_NOTES.md" \
  "docs/runbooks/QUICK_START.md" \
  "docs/runbooks/INSTALLATION.md" \
  "docs/runbooks/OPERATIONS_INDEX.md" \
  "docs/runbooks/OPERATOR_HANDOFF.md" \
  "docs/runbooks/ROLLBACK_RUNBOOK.md"; do
  if [[ -f "$f" ]]; then
    pass "Required file exists: $f"
  else
    fail "Required file missing: $f"
  fi
done

echo ""
echo "--- VERSION Check ---"
VERSION=$(cat VERSION 2>/dev/null || echo "")
if [[ "$VERSION" == "0.42.0-rc1" ]]; then
  pass "VERSION is 0.42.0-rc1"
else
  fail "VERSION is '$VERSION', expected '0.42.0-rc1'"
fi

echo ""
echo "--- Release Decision GO ---"
RELEASE_DOC="docs/releases/PHASE37_RELEASE_READINESS.md"
if [[ -f "$RELEASE_DOC" ]]; then
  if grep -q "Status:.*GO" "$RELEASE_DOC" 2>/dev/null; then
    pass "Release decision is GO in $RELEASE_DOC"
  else
    fail "Release decision is not GO in $RELEASE_DOC"
  fi
else
  fail "Release readiness doc not found at $RELEASE_DOC"
fi

echo ""
echo "--- Safety Locks Documented ---"
ENV_FILE=".env.example"
if [[ -f "$ENV_FILE" ]]; then
  LOCKS_PASS=0
  LOCKS_FAIL=0
  for pair in "DRY_RUN=true" "LIVE_TRADING_ACK=false" "MT5_ENABLED=false" "PRODUCTION_ALLOW_LIVE_ACTIONS=false" "RISK_GUARDIAN_ENABLED=true"; do
    key="${pair%%=*}"
    expected="${pair#*=}"
    if grep -Eq "^\s*${key}\s*=\s*${expected}\s*" "$ENV_FILE" 2>/dev/null; then
      LOCKS_PASS=$((LOCKS_PASS + 1))
    else
      LOCKS_FAIL=$((LOCKS_FAIL + 1))
      fail "Safety lock ${key}=${expected} not found in $ENV_FILE"
    fi
  done
  if [[ "$LOCKS_FAIL" -eq 0 ]]; then
    pass "All 5 safety locks documented in $ENV_FILE ($LOCKS_PASS/$LOCKS_PASS)"
  fi
else
  fail ".env.example not found"
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
echo "--- README.md Content Checks ---"
README_OK=true
for phrase in "Quick Start" "Feature Map" "Architecture Summary" "Operator Handoff" "Server Commands" "Validation Commands" "Safety-First" "0.42.0-rc1"; do
  if grep -qi "$phrase" README.md 2>/dev/null; then
    true
  else
    fail "README.md missing section: $phrase"
    README_OK=false
  fi
done
if $README_OK; then
  pass "README.md contains all required sections"
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS, Failed: $FAIL"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
