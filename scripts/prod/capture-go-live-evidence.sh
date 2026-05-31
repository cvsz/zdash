#!/usr/bin/env bash
set -euo pipefail

ZDASH_RUNTIME="${ZDASH_PROD_RUNTIME:-/opt/zdash/runtime}"
EVIDENCE_DIR="${ZDASH_EVIDENCE_DIR:-docs/reports/generated}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PASS=0
FAIL=0

pass() { echo "PASSED: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAILED: $1"; FAIL=$((FAIL + 1)); }

echo "=== Go-Live Evidence Capture ==="
echo "Timestamp: $TIMESTAMP"
echo "Evidence directory: $EVIDENCE_DIR"
echo ""

if [[ ! -d "$ZDASH_RUNTIME" ]]; then
  echo "FAILED: Production runtime not found at $ZDASH_RUNTIME"
  echo "Run: sudo ./install-zdash-prod.sh"
  exit 1
fi

mkdir -p "$EVIDENCE_DIR"

EVIDENCE_FILE="$EVIDENCE_DIR/go-live-evidence-$(date -u +%Y%m%d-%H%M%S).md"
echo "Writing evidence to: $EVIDENCE_FILE"
echo ""

{
  echo "# Go-Live Evidence Capture"
  echo ""
  echo "Generated: $TIMESTAMP"
  echo "Runtime: $ZDASH_RUNTIME"
  echo ""
  echo "## Service Status"
  echo ""
  echo '```'
} >> "$EVIDENCE_FILE"

echo "--- Capturing Service Status ---"
{
  echo "=== zdash.service status ==="
  systemctl status zdash --no-pager 2>&1 || echo "(zdash.service not found)"
} >> "$EVIDENCE_FILE"
pass "Captured zdash.service status"

{
  echo ""
  echo "=== Docker Compose Services ==="
  COMPOSE_FILE="${ZDASH_PROD_COMPOSE:-$ZDASH_RUNTIME/docker-compose.yml}"
  if [[ -f "$COMPOSE_FILE" ]]; then
    docker compose -f "$COMPOSE_FILE" ps 2>&1 || echo "(docker compose not available)"
  else
    echo "(compose file not found at $COMPOSE_FILE)"
  fi
} >> "$EVIDENCE_FILE"
pass "Captured Docker Compose status"

echo ""
echo "--- Capturing Health ---"
{
  echo ""
  echo "## Health Checks"
  echo ""
  echo '```'
  echo "=== Backend Health ==="
  curl -s --max-time 5 http://localhost:8005/health 2>&1 || echo "(backend health unreachable)"
  echo ""
  echo "=== Backend Safety Check ==="
  curl -s --max-time 5 http://localhost:8005/api/admin/safety-check 2>&1 || echo "(safety check unreachable)"
  echo ""
  echo "=== Frontend Status ==="
  curl -s -o /dev/null -w "HTTP %{http_code}" --max-time 5 http://localhost:5173 2>&1 || echo "(frontend unreachable)"
  echo ""
  echo '```'
} >> "$EVIDENCE_FILE"
pass "Captured health checks"

echo ""
echo "--- Capturing Safety Locks ---"
{
  echo ""
  echo "## Safety Locks"
  echo ""
  echo '```'
  ENV_FILE="${ZDASH_PROD_ENV:-$ZDASH_RUNTIME/.env.production}"
  if [[ -f "$ENV_FILE" ]]; then
    echo "DRY_RUN=$(grep -s '^DRY_RUN=' "$ENV_FILE" | cut -d= -f2)" || echo "DRY_RUN=(unset)"
    echo "LIVE_TRADING_ACK=$(grep -s '^LIVE_TRADING_ACK=' "$ENV_FILE" | cut -d= -f2)" || echo "LIVE_TRADING_ACK=(unset)"
    echo "MT5_ENABLED=$(grep -s '^MT5_ENABLED=' "$ENV_FILE" | cut -d= -f2)" || echo "MT5_ENABLED=(unset)"
    echo "PRODUCTION_ALLOW_LIVE_ACTIONS=$(grep -s '^PRODUCTION_ALLOW_LIVE_ACTIONS=' "$ENV_FILE" | cut -d= -f2)" || echo "PRODUCTION_ALLOW_LIVE_ACTIONS=(unset)"
    echo "RISK_GUARDIAN_ENABLED=$(grep -s '^RISK_GUARDIAN_ENABLED=' "$ENV_FILE" | cut -d= -f2)" || echo "RISK_GUARDIAN_ENABLED=(unset)"
    echo "BACKEND_PORT=$(grep -s '^BACKEND_PORT=' "$ENV_FILE" | cut -d= -f2)" || echo "BACKEND_PORT=8005"
  else
    echo "(env file not found at $ENV_FILE)"
  fi
  echo '```'
} >> "$EVIDENCE_FILE"
pass "Captured safety lock values (no secrets printed)"

echo ""
echo "--- Capturing Validation Evidence ---"
{
  echo ""
  echo "## Validation Summary"
  echo ""
  echo "- Backend health: $(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://localhost:8005/health 2>/dev/null || echo 'unreachable')"
  echo "- Frontend status: $(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://localhost:5173 2>/dev/null || echo 'unreachable')"
  echo "- zdash.service: $(systemctl is-active zdash 2>/dev/null || echo 'not found')"
  echo ""
  echo "## Documentation Verified"
  echo ""
  echo "- Rollback runbook: $(test -f docs/runbooks/ROLLBACK_RUNBOOK.md && echo 'found' || echo 'missing')"
  echo "- Go-live checklist: $(test -f docs/runbooks/GO_LIVE_CHECKLIST.md && echo 'found' || echo 'missing')"
  echo "- Production dry-run: $(test -f docs/runbooks/PRODUCTION_DRY_RUN_VERIFICATION.md && echo 'found' || echo 'missing')"
  echo "- Realtime gateway: $(test -f docs/runbooks/REALTIME_GATEWAY.md && echo 'found' || echo 'missing')"
  echo "- Release readiness: $(test -f docs/releases/PHASE37_RELEASE_READINESS.md && echo 'found' || echo 'missing')"
  echo "- Go-live rehearsal: $(test -f docs/runbooks/GO_LIVE_REHEARSAL.md && echo 'found' || echo 'missing')"
  echo ""
  echo "---"
  echo "*Evidence captured by: scripts/prod/capture-go-live-evidence.sh*"
} >> "$EVIDENCE_FILE"
pass "Captured validation evidence"

echo ""
echo "=== Evidence Capture Results ==="
echo "Evidence file: $EVIDENCE_FILE"
echo "Passed: $PASS, Failed: $FAIL"
