#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "zDash healthcheck"
git status --short || true

if [ -d "backend" ]; then
  bash .codex/cloud/repair-backend-deps.sh
  cd backend
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m ruff check app tests
  python -B -m pytest -q
  cd "$ROOT_DIR"
fi

if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
  if [ -s "$HOME/.nvm/nvm.sh" ]; then
    # shellcheck disable=SC1091
    source "$HOME/.nvm/nvm.sh"
    nvm use 20 >/dev/null || nvm install 20 >/dev/null
  fi
  cd frontend
  npm install --legacy-peer-deps --no-audit --fund=false
  npm test
  npm run build
  cd "$ROOT_DIR"
fi
