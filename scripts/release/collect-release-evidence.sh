#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EVIDENCE_DIR="docs/reports/generated"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
RELEASE_TAG="${RELEASE_TAG:-v2.1.0-rc1}"
PASS=0
FAIL=0

pass() { echo "PASSED: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAILED: $1"; FAIL=$((FAIL + 1)); }

echo "=== Release Evidence Collection ==="
echo "Release tag: $RELEASE_TAG"
echo "Timestamp: $TIMESTAMP"
echo ""

mkdir -p "$EVIDENCE_DIR"

EVIDENCE_FILE="$EVIDENCE_DIR/release-evidence-$RELEASE_TAG-$(date -u +%Y%m%d-%H%M%S).md"
echo "Writing evidence to: $EVIDENCE_FILE"
echo ""

{
  echo "# Release Evidence Archive"
  echo ""
  echo "Release: $RELEASE_TAG"
  echo "Generated: $TIMESTAMP"
  echo ""
  echo "## Validation Results"
  echo ""
} >> "$EVIDENCE_FILE"
pass "Created evidence file"

echo "--- Collecting Validation Evidence ---"
{
  echo '```'
  echo "=== Backend Tests ==="
  if cd backend && python -B -m pytest -q 2>&1 | tail -5; then
    cd "$SCRIPT_DIR/../.."
  else
    cd "$SCRIPT_DIR/../.." || true
    echo "(backend test collection attempted)"
  fi
  echo ""
  echo "=== Frontend Tests ==="
  if cd frontend && npm test 2>&1 | tail -10; then
    cd "$SCRIPT_DIR/../.."
  else
    cd "$SCRIPT_DIR/../.." || true
    echo "(frontend test collection attempted)"
  fi
  echo '```'
} >> "$EVIDENCE_FILE"
pass "Collected validation evidence"

echo "--- Collecting Makefile Targets ---"
{
  echo ""
  echo "## Makefile Targets"
  echo ""
  echo '```'
  grep -E '^\.PHONY:' Makefile | sort
  echo '```'
} >> "$EVIDENCE_FILE"
pass "Collected Makefile targets"

echo "--- Collecting Scripts Inventory ---"
{
  echo ""
  echo "## Scripts Inventory"
  echo ""
  echo '```'
  git ls-files 'scripts/*.sh' 'scripts/**/*.sh' | sort
  echo '```'
} >> "$EVIDENCE_FILE"
pass "Collected script inventory"

echo "--- Collecting Documentation Inventory ---"
{
  echo ""
  echo "## Documentation Inventory"
  echo ""
  echo '```'
  git ls-files 'docs/*.md' 'docs/**/*.md' | sort
  echo '```'
} >> "$EVIDENCE_FILE"
pass "Collected documentation inventory"

echo "--- Collecting Phase Doc Inventory ---"
{
  echo ""
  echo "## Phase Artifacts"
  echo ""
  echo '```'
  echo "Phase 38 (Release Readiness):"
  for f in docs/releases/PHASE37_RELEASE_READINESS.md docs/runbooks/ROLLBACK_RUNBOOK.md docs/reports/PHASE_TRACEABILITY_MATRIX.md docs/runbooks/GO_LIVE_CHECKLIST.md; do
    if [[ -f "$f" ]]; then echo "  EXISTS: $f"; else echo "  MISSING: $f"; fi
  done
  echo ""
  echo "Phase 39 (Dry-Run):"
  for f in docs/runbooks/PRODUCTION_DRY_RUN_VERIFICATION.md docs/reports/PHASE39_PRODUCTION_DRY_RUN_REPORT.md scripts/prod/verify-prod-runtime.sh scripts/prod/verify-prod-health.sh scripts/prod/verify-prod-rollback-readiness.sh scripts/prod/verify-prod-observability.sh; do
    if [[ -f "$f" ]]; then echo "  EXISTS: $f"; else echo "  MISSING: $f"; fi
  done
  echo ""
  echo "Phase 40 (Rehearsal):"
  for f in docs/runbooks/GO_LIVE_REHEARSAL.md docs/reports/PHASE40_GO_LIVE_REHEARSAL_REPORT.md scripts/prod/verify-go-live-safety-locks.sh scripts/prod/capture-go-live-evidence.sh scripts/prod/run-go-live-rehearsal.sh; do
    if [[ -f "$f" ]]; then echo "  EXISTS: $f"; else echo "  MISSING: $f"; fi
  done
  echo ""
  echo "Phase 41 (Release):"
  for f in docs/releases/PHASE41_RELEASE_CANDIDATE.md docs/runbooks/OPERATOR_HANDOFF.md docs/reports/PHASE41_RELEASE_EVIDENCE_ARCHIVE.md scripts/release/verify-release-readiness.sh scripts/release/collect-release-evidence.sh scripts/release/create-release-candidate.sh; do
    if [[ -f "$f" ]]; then echo "  EXISTS: $f"; else echo "  MISSING: $f"; fi
  done
  echo '```'
} >> "$EVIDENCE_FILE"
pass "Collected phase artifact inventory"

echo "--- Collecting Safety Lock Documentation ---"
{
  echo ""
  echo "## Safety Locks"
  echo ""
  echo '```'
  ENV_FILE=".env.example"
  if [[ -f "$ENV_FILE" ]]; then
    echo "DRY_RUN: $(grep -s '^DRY_RUN=' "$ENV_FILE" | cut -d= -f2 || echo 'not found')"
    echo "LIVE_TRADING_ACK: $(grep -s '^LIVE_TRADING_ACK=' "$ENV_FILE" | cut -d= -f2 || echo 'not found')"
    echo "MT5_ENABLED: $(grep -s '^MT5_ENABLED=' "$ENV_FILE" | cut -d= -f2 || echo 'not found')"
    echo "PRODUCTION_ALLOW_LIVE_ACTIONS: $(grep -s '^PRODUCTION_ALLOW_LIVE_ACTIONS=' "$ENV_FILE" | cut -d= -f2 || echo 'not found')"
    echo "RISK_GUARDIAN_ENABLED: $(grep -s '^RISK_GUARDIAN_ENABLED=' "$ENV_FILE" | cut -d= -f2 || echo 'not found')"
  fi
  echo '```'
} >> "$EVIDENCE_FILE"
pass "Collected safety lock documentation"

{
  echo ""
  echo "---"
  echo "*Evidence collected by: scripts/release/collect-release-evidence.sh*"
  echo "*Timestamp: $TIMESTAMP*"
} >> "$EVIDENCE_FILE"

echo ""
echo "=== Evidence Collection Results ==="
echo "Evidence file: $EVIDENCE_FILE"
echo "Passed: $PASS, Failed: $FAIL"
