#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
echo "zDash healthcheck"
git status --short || true
if [ -d "backend" ]; then
  if [ -f ".codex/cloud/repair-backend-deps.sh" ]; then
    bash .codex/cloud/repair-backend-deps.sh
  fi
  cd backend
  if [ -d ".venv" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  fi
  pytest
  cd "$ROOT_DIR"
fi
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
  cd frontend
  npm install --legacy-peer-deps --no-audit --fund=false
  npm test -- --run
  npm run build
  cd "$ROOT_DIR"
fi
