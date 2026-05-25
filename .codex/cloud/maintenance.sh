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

printf '\n[1/4] Backend tests\n'
if [ -d "backend" ]; then
  cd backend
  if [ -d ".venv" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  fi
  pytest | tee -a "$ROOT_DIR/$REPORT"
  cd "$ROOT_DIR"
else
  echo "No backend directory found." | tee -a "$REPORT"
fi

printf '\n[2/4] Frontend tests\n'
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
  cd frontend
  npm test -- --run | tee -a "$ROOT_DIR/$REPORT"
  cd "$ROOT_DIR"
else
  echo "No frontend package found." | tee -a "$REPORT"
fi

printf '\n[3/4] Frontend build\n'
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
  cd frontend
  npm run build | tee -a "$ROOT_DIR/$REPORT"
  cd "$ROOT_DIR"
else
  echo "No frontend package found." | tee -a "$REPORT"
fi

printf '\n[4/4] Basic secret-pattern scan\n'
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

echo "Maintenance complete: $REPORT"
