#!/usr/bin/env bash
set -Eeuo pipefail

printf '\n============================================================\n'
printf 'zDash Codex Cloud Setup\n'
printf '============================================================\n'

ROOT_DIR="${CODEX_WORKSPACE_DIR:-$(pwd)}"
cd "$ROOT_DIR"

step() {
  printf '\n[%s]\n' "$1"
}

step "1/10 Repository context"
pwd
git status --short || true
git branch --show-current || true
git rev-parse --short HEAD || true

step "2/10 Runtime info"
uname -a || true
python3 --version || true
node --version || true
npm --version || true

step "3/10 Helper directories"
mkdir -p .codex/logs .codex/reports docs/prompt

step "4/10 Backend dependency repair"
if [ -d "backend" ]; then
  if [ -f ".codex/cloud/repair-backend-deps.sh" ]; then
    bash .codex/cloud/repair-backend-deps.sh
  else
    echo "Missing .codex/cloud/repair-backend-deps.sh" >&2
    exit 1
  fi
else
  echo "No backend directory found."
fi

step "5/10 Frontend dependency install (Node 20)"
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
  if [ -s "$HOME/.nvm/nvm.sh" ]; then
    # shellcheck disable=SC1091
    source "$HOME/.nvm/nvm.sh"
    nvm use 20 >/dev/null || nvm install 20 >/dev/null
  fi
  cd frontend
  npm install --legacy-peer-deps --no-audit --fund=false
  cd "$ROOT_DIR"
else
  echo "No frontend package found."
fi

step "6/10 Safe env bootstrap"
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env from .env.example (review values before runtime use)."
fi
if [ -f "frontend/.env.example" ] && [ ! -f "frontend/.env" ]; then
  cp frontend/.env.example frontend/.env
  echo "Created frontend/.env from frontend/.env.example."
fi

step "7/10 Helper script generation"
cat > .codex/run-phase.sh <<'RUNPHASE'
#!/usr/bin/env bash
set -Eeuo pipefail
TARGET="${1:-}"
if [ -z "$TARGET" ]; then
  echo "Usage: bash .codex/run-phase.sh <phase-number-or-prompt-file>"
  echo "Examples:"
  echo "  bash .codex/run-phase.sh 08"
  echo "  bash .codex/run-phase.sh docs/prompt/codex-runs/phase08.5.prompt"
  exit 1
fi

if [ -f "$TARGET" ]; then
  PROMPT="$TARGET"
elif [[ "$TARGET" =~ ^[0-9]+$ ]]; then
  PHASE_PADDED=$(printf "%02d" "$TARGET")
  PROMPT="docs/prompt/phase${PHASE_PADDED}.prompt"
else
  PROMPT="docs/prompt/${TARGET}"
fi

if [ ! -f "$PROMPT" ]; then
  echo "Prompt not found: $PROMPT"
  find docs/prompt -maxdepth 3 -type f -name "*.prompt" | sort || true
  exit 1
fi

cat "$PROMPT"
RUNPHASE
chmod +x .codex/run-phase.sh

cat > .codex/healthcheck.sh <<'HEALTH'
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
HEALTH
chmod +x .codex/healthcheck.sh

cat > .codex/maintenance.sh <<'MAIN'
#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
bash .codex/cloud/maintenance.sh
MAIN
chmod +x .codex/maintenance.sh

step "8/10 AGENTS bootstrap (if missing)"
if [ ! -f "AGENTS.md" ] && [ -f ".codex/cloud/AGENTS.template.md" ]; then
  cp .codex/cloud/AGENTS.template.md AGENTS.md
fi

step "9/10 Initial validation"
set +e
bash .codex/healthcheck.sh
STATUS="$?"
set -e
if [ "$STATUS" -ne 0 ]; then
  echo "Initial healthcheck failed. Continue with targeted fixes in task workflow."
fi

step "10/10 Complete"
printf '\n============================================================\n'
printf 'zDash Codex Cloud Setup Complete\n'
printf '============================================================\n'

exit 0
