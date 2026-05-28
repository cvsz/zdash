#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="${CODEX_WORKSPACE_DIR:-$(pwd)}"
cd "$ROOT_DIR"
ROOT_DIR="$(pwd)"

printf '\n============================================================\n'
printf 'zDash Codex Cloud Maintenance\n'
printf '============================================================\n'

mkdir -p "$ROOT_DIR/.codex/reports" "$ROOT_DIR/.codex/logs"
REPORT="$ROOT_DIR/.codex/reports/codex-maintenance-$(date -u +%Y%m%dT%H%M%SZ).md"

scan_excludes=(
  --exclude-dir=.git
  --exclude-dir=node_modules
  --exclude-dir=.venv
  --exclude-dir=dist
  --exclude-dir=.gnupg
  --exclude-dir=.ssh
  --exclude-dir=.codex/reports
  --exclude-dir=.codex/logs
  --exclude-dir=.codex/cache
  --exclude-dir=.codex/tmp
  --exclude="*.prompt"
  --exclude="*.lock"
  --exclude="*.sock"
)

{
  echo "# zDash Codex Cloud Maintenance Report"
  echo
  echo "- Date UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "- Repo: cvsz/zdash"
  echo "- Baseline: Phase 01-10 plus Phase 7.10 collaboration/federation foundation"
  echo "- Cloudflare operator repo: cvsz/zeaz-platform"
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

{
  echo
  echo "## Static baseline checks"
  echo '```'
  echo "backend port references:"
  grep -RIn "localhost:8000\|:8000\|BACKEND_PORT=8000" "${scan_excludes[@]}" . || true
  echo
  echo "Cloudflare operator refs:"
  grep -RIn "cvsz/zeaz-platform\|zdash.zeaz.dev\|CLOUDFLARE_OPERATOR_REPO" README.md .env.example .codex/cloud 2>/dev/null || true
  echo '```'
} >> "$REPORT"

if grep -RIn "localhost:8000\|BACKEND_PORT=8000" "${scan_excludes[@]}" . >/tmp/zdash-codex-port8000.txt 2>/dev/null; then
  echo "FAILED: old backend port 8000 found outside prompt archives" | tee -a "$REPORT"
  cat /tmp/zdash-codex-port8000.txt | tee -a "$REPORT"
  status=1
else
  echo "PASSED: no old backend port 8000 found outside prompt archives" | tee -a "$REPORT"
fi

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
  if [ -f "infra/docker/nginx.Dockerfile" ]; then
    run_step "docker nginx build" docker build -f infra/docker/nginx.Dockerfile . || status=1
  fi
  run_step "docker compose config" docker compose config || status=1
  if [ -f "docker-compose.prod.yml" ]; then
    run_step "docker compose prod config" docker compose -f docker-compose.prod.yml config || status=1
  fi
else
  echo "Docker not available; skipping Docker validation." | tee -a "$REPORT"
fi

{
  echo
  echo "## Basic secret-pattern scan"
  echo '```'
  grep -RInE "(GPG_PASSPHRASE|sk-[A-Za-z0-9_-]{20,}|api[_-]?key=|password=|private key|BEGIN RSA|BEGIN OPENSSH|STRIPE_SECRET|CLOUDFLARE_API_TOKEN|TUNNEL_TOKEN|ZONE_ID=|ACCOUNT_ID=)" "${scan_excludes[@]}" . || true
  echo '```'
  echo
  echo "## Current hardening watchlist"
  echo
  echo "- Verify backend manifests include psycopg[binary] for postgresql+psycopg:// runtime."
  echo "- Verify collaboration WebSocket auth when AUTH_ENABLED=true."
  echo "- Verify workspace federation mutation endpoints require auth/RBAC."
  echo "- Verify frontend WS base URL derives from VITE_WS_BASE_URL or VITE_API_BASE_URL."
} >> "$REPORT"

printf '\nMaintenance complete: %s\n' "$REPORT"
exit "$status"
