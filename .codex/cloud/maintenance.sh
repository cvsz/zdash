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

if [ -d "backend" ]; then
  run_step "backend dependency repair" bash .codex/cloud/repair-backend-deps.sh || status=1
  cd backend
  # shellcheck disable=SC1091
  source .venv/bin/activate
  run_step "backend lint" python -m ruff check app tests || status=1
  run_step "backend tests" python -B -m pytest -q || status=1
  cd "$ROOT_DIR"
else
  echo "No backend directory found." | tee -a "$REPORT"
fi

if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
  if [ -s "$HOME/.nvm/nvm.sh" ]; then
    # shellcheck disable=SC1091
    source "$HOME/.nvm/nvm.sh"
    run_step "node version switch" nvm use 20 || status=1
  fi
  cd frontend
  run_step "frontend dependency install" npm install --legacy-peer-deps --no-audit --fund=false || status=1
  run_step "frontend tests" npm test || status=1
  run_step "frontend build" npm run build || status=1
  cd "$ROOT_DIR"
else
  echo "No frontend package found." | tee -a "$REPORT"
fi

if command -v docker >/dev/null 2>&1; then
  run_step "docker backend build" docker build -f infra/docker/backend.Dockerfile . || status=1
  run_step "docker frontend build" docker build -f infra/docker/frontend.Dockerfile . || status=1
  run_step "docker compose config" docker compose config || status=1
else
  echo "Docker not available; skipping Docker validation." | tee -a "$REPORT"
fi

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

printf '\nMaintenance complete: %s\n' "$REPORT"
exit "$status"
