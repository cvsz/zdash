#!/usr/bin/env bash
set -Eeuo pipefail

printf '\n============================================================\n'
printf 'zDash Codex Cloud Setup\n'
printf '============================================================\n'

ROOT_DIR="${CODEX_WORKSPACE_DIR:-$(pwd)}"
cd "$ROOT_DIR"

printf '\n[1/9] Repository context\n'
pwd
git status --short || true
git branch --show-current || true
git rev-parse --short HEAD || true

printf '\n[2/9] Runtime info\n'
uname -a || true
python3 --version || true
node --version || true
npm --version || true

printf '\n[3/9] Helper directories\n'
mkdir -p .codex/logs .codex/reports docs/prompt

printf '\n[4/9] Backend dependencies\n'
if [ -d "backend" ]; then
  if [ -f ".codex/cloud/repair-backend-deps.sh" ]; then
    bash .codex/cloud/repair-backend-deps.sh
  else
    cd backend
    if [ ! -d ".venv" ]; then
      python3 -m venv .venv
    fi
    # shellcheck disable=SC1091
    source .venv/bin/activate
    python -m pip install --upgrade pip setuptools wheel
    if [ -f "pyproject.toml" ]; then
      pip install -e ".[dev]" || pip install -e .
    elif [ -f "requirements.txt" ]; then
      pip install -r requirements.txt
    else
      echo "No backend dependency file found. Skipping backend install."
    fi
    cd "$ROOT_DIR"
  fi
else
  echo "No backend directory found."
fi

printf '\n[5/9] Frontend dependencies\n'
if [ -d "frontend" ]; then
  cd frontend
  if [ -f "package-lock.json" ]; then
    npm ci || npm install
  elif [ -f "package.json" ]; then
    npm install
  else
    echo "No frontend package.json found."
  fi
  cd "$ROOT_DIR"
else
  echo "No frontend directory found."
fi

printf '\n[6/9] Safe env bootstrap\n'
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Review before runtime use."
fi
if [ -f "frontend/.env.example" ] && [ ! -f "frontend/.env" ]; then
  cp frontend/.env.example frontend/.env
  echo "Created frontend/.env from frontend/.env.example."
fi

printf '\n[7/9] Codex helper scripts\n'
cat > .codex/run-phase.sh <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail
PHASE="${1:-}"
if [ -z "$PHASE" ]; then
  echo "Usage: bash .codex/run-phase.sh 24"
  exit 1
fi
PROMPT="docs/prompt/phase${PHASE}.prompt"
if [ ! -f "$PROMPT" ]; then
  echo "Prompt not found: $PROMPT"
  find docs/prompt -maxdepth 1 -type f -name "*.prompt" | sort || true
  exit 1
fi
cat "$PROMPT"
EOF
chmod +x .codex/run-phase.sh

cat > .codex/healthcheck.sh <<'EOF'
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
  npm test -- --run
  npm run build
  cd "$ROOT_DIR"
fi
EOF
chmod +x .codex/healthcheck.sh

cat > .codex/maintenance.sh <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
mkdir -p .codex/reports
REPORT=".codex/reports/maintenance-$(date -u +%Y%m%dT%H%M%SZ).md"
{
  echo "# zDash Maintenance Report"
  echo
  echo "- Date UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "- Branch: $(git branch --show-current 2>/dev/null || true)"
  echo "- Commit: $(git rev-parse --short HEAD 2>/dev/null || true)"
  echo
  echo "## Git status"
  echo '```'
  git status --short || true
  echo '```'
  echo
  echo "## Prompt files"
  echo '```'
  find docs/prompt -maxdepth 1 -type f | sort || true
  echo '```'
} > "$REPORT"
set +e
bash .codex/healthcheck.sh | tee -a "$REPORT"
STATUS="${PIPESTATUS[0]}"
set -e
echo "Maintenance report: $REPORT"
exit "$STATUS"
EOF
chmod +x .codex/maintenance.sh

printf '\n[8/9] AGENTS.md bootstrap\n'
if [ ! -f "AGENTS.md" ]; then
  cp .codex/cloud/AGENTS.template.md AGENTS.md 2>/dev/null || true
fi

printf '\n[9/9] Initial validation\n'
bash .codex/healthcheck.sh || {
  echo "Initial healthcheck failed after dependency repair. Codex should fix test/code issues next."
}

printf '\n============================================================\n'
printf 'zDash Codex Cloud Setup Complete\n'
printf '============================================================\n'
