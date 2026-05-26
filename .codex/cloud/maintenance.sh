#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="${CODEX_WORKSPACE_DIR:-$(pwd)}"
cd "$ROOT_DIR"

printf '\n============================================================\n'
printf 'zDash Codex Cloud Maintenance\n'
printf '============================================================\n'

mkdir -p .codex/reports .codex/logs
REPORT=".codex/reports/codex-maintenance-$(date -u +%Y%m%dT%H%M%SZ).md"

{
  echo "# zDash Codex Cloud Maintenance Report"
  echo
  echo "- Date UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "- Repo: cvsz/zdash"
  echo "- Branch: $(git branch --show-current 2>/dev/null || true)"
  echo "- Commit: $(git rev-parse --short HEAD 2>/dev/null || true)"
  echo
  echo "## Git status"
  echo '```'
  git status --short || true
  echo '```'
  echo
  echo "## Prompt inventory"
  echo '```'
  find docs/prompt -maxdepth 1 -type f | sort || true
  echo '```'
  echo
  echo "## Backend inventory"
  echo '```'
  find backend/app -maxdepth 2 -type d | sort 2>/dev/null || true
  echo '```'
  echo
  echo "## Frontend inventory"
  echo '```'
  find frontend/src -maxdepth 2 -type d | sort 2>/dev/null || true
  echo '```'
} > "$REPORT"

run_step() {
  local name="$1"
  shift
  printf '\n[%s]\n' "$name"
  set +e
  "$@" 2>&1 | tee -a "$REPORT"
  local step_status="${PIPESTATUS[0]}"
  set -e
  if [ "$step_status" -ne 0 ]; then
    echo "FAILED: $name status=$step_status" | tee -a "$REPORT"
    return "$step_status"
  fi
  echo "PASSED: $name" | tee -a "$REPORT"
  return 0
}

status=0

printf '\n[0/6] Backend dependency repair\n'
if [ -d "backend" ] && [ -f ".codex/cloud/repair-backend-deps.sh" ]; then
  run_step "backend dependency repair" bash .codex/cloud/repair-backend-deps.sh || status=1
elif [ -d "backend" ]; then
  echo "No repair helper found; continuing to backend tests." | tee -a "$REPORT"
else
  echo "No backend directory found." | tee -a "$REPORT"
fi

printf '\n[1/6] Backend tests\n'
if [ -d "backend" ]; then
  cd backend
  if [ -d ".venv" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  fi
  run_step "backend pytest" pytest || status=1
  cd "$ROOT_DIR"
else
  echo "No backend directory found." | tee -a "$REPORT"
fi

printf '\n[2/6] Frontend dependency install\n'
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
  cd frontend
  run_step "frontend dependency install" npm install --legacy-peer-deps --no-audit --fund=false || status=1
  cd "$ROOT_DIR"
else
  echo "No frontend package found." | tee -a "$REPORT"
fi

printf '\n[3/6] Frontend tests\n'
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
  cd frontend
  run_step "frontend tests" npm test || status=1
  cd "$ROOT_DIR"
else
  echo "No frontend package found." | tee -a "$REPORT"
fi

printf '\n[4/6] Frontend build\n'
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
  cd frontend
  run_step "frontend build" npm run build || status=1
  cd "$ROOT_DIR"
else
  echo "No frontend package found." | tee -a "$REPORT"
fi

printf '\n[5/6] Basic secret-pattern scan\n'
{
  echo
  echo "## Basic secret-pattern scan"
  echo '```'
  grep -RInE "(sk-[A-Za-z0-9_-]{20,}|api[_-]?key=|password=|private key|BEGIN RSA|BEGIN OPENSSH|STRIPE_SECRET|CLOUDFLARE_API_TOKEN)" \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude-dir=.venv \
    --exclude-dir=dist \
    . || true
  echo '```'
} >> "$REPORT"

printf '\n[6/6] Result\n'
echo "Maintenance complete: $REPORT"
exit "$status"
