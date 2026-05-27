#!/usr/bin/env bash
set -Eeuo pipefail

# ============================================================
# zDash Full-Stack Installer / Repair / Validator
# Target: Ubuntu 22.04/24.04 VM
# Repo:   ~/zdash or https://github.com/cvsz/zdash.git
# ============================================================

ROOT="${ROOT:-$HOME/zdash}"
REPO_URL="${REPO_URL:-git@github.com:cvsz/zdash.git}"
BACKEND_PORT="${BACKEND_PORT:-8005}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
DO_PULL="${DO_PULL:-false}"
RUN_DOCKER_BUILDS="${RUN_DOCKER_BUILDS:-false}"
START_SERVICES="${START_SERVICES:-false}"

log() {
  printf '\n\033[1;36m[%s]\033[0m %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

warn() {
  printf '\n\033[1;33m[WARN]\033[0m %s\n' "$*"
}

die() {
  printf '\n\033[1;31m[ERROR]\033[0m %s\n' "$*"
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || return 1
}

apt_install() {
  if need_cmd sudo; then
    sudo apt-get update
    sudo apt-get install -y "$@"
  else
    apt-get update
    apt-get install -y "$@"
  fi
}

log "zDash full-stack installer starting"

# Avoid env token overriding gh/git auth.
unset GITHUB_TOKEN || true
unset GH_TOKEN || true

log "Installing system packages"
apt_install \
  git \
  curl \
  ca-certificates \
  build-essential \
  pkg-config \
  python3 \
  python3-venv \
  python3-pip \
  python3-dev \
  nodejs \
  npm

log "System versions"
git --version || true
"$PYTHON_BIN" --version || true
node --version || true
npm --version || true

if [ ! -d "$ROOT/.git" ]; then
  log "Cloning zDash into $ROOT"
  mkdir -p "$(dirname "$ROOT")"
  git clone "$REPO_URL" "$ROOT" || {
    warn "SSH clone failed. Trying HTTPS."
    git clone "https://github.com/cvsz/zdash.git" "$ROOT"
  }
else
  log "Using existing repo: $ROOT"
fi

cd "$ROOT"

log "Git status before install"
git status --short || true

if [ "$DO_PULL" = "true" ]; then
  if [ -n "$(git status --porcelain)" ]; then
    warn "Working tree has local changes. Skipping git pull to avoid overwriting work."
    warn "Commit or stash first, then run: DO_PULL=true bash install-zdash-fullstack.sh"
  else
    log "Pulling latest main"
    git pull --rebase
  fi
fi

log "Ensuring .env exists"
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp .env.example .env
fi

log "Forcing safe local defaults"
{
  echo ""
  echo "# zDash local installer defaults"
  echo "BACKEND_PORT=$BACKEND_PORT"
  echo "DRY_RUN=true"
  echo "LIVE_TRADING_ACK=false"
  echo "RISK_GUARDIAN_ENABLED=true"
  echo "MT5_ENABLED=false"
  echo "IOT_DRY_RUN=true"
  echo "SOCIAL_DRY_RUN=true"
  echo "SOCIAL_AUTO_POST_ENABLED=false"
  echo "ALLOW_STRATEGY_PROMOTION=false"
  echo "MULTI_TENANT_ENABLED=false"
} >> .env

log "Backend setup"
cd "$ROOT/backend"

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel

if [ -f "pyproject.toml" ]; then
  log "Installing backend package with dev extras"
  python -m pip install -e '.[dev]' || {
    warn "pip install -e .[dev] failed. Trying requirements fallback."
    [ -f requirements.txt ] && python -m pip install -r requirements.txt
  }
elif [ -f "requirements.txt" ]; then
  log "Installing backend requirements"
  python -m pip install -r requirements.txt
fi

log "Installing required dev tools"
python -m pip install --upgrade ruff pytest pytest-cov httpx

log "Backend lint auto-fix"
python -m ruff check . --fix || true

log "Backend lint check"
python -m ruff check . || warn "Ruff still reports issues. Review output above."

log "Backend tests"
python -B -m pytest -q

log "Frontend setup"
cd "$ROOT/frontend"

if [ -f ".npmrc" ]; then
  log "Using existing frontend/.npmrc"
else
  echo "legacy-peer-deps=true" > .npmrc
fi

npm install --legacy-peer-deps --no-audit --fund=false

log "Frontend tests"
npm test

log "Frontend build"
npm run build

cd "$ROOT"

if [ "$RUN_DOCKER_BUILDS" = "true" ]; then
  if need_cmd docker; then
    log "Docker backend build"
    docker build -f infra/docker/backend.Dockerfile .

    log "Docker frontend build"
    docker build -f infra/docker/frontend.Dockerfile .
  else
    warn "Docker not found. Skipping Docker builds."
  fi
fi

log "Creating helper scripts"

cat > run-backend.sh <<RUNBACKEND
#!/usr/bin/env bash
set -Eeuo pipefail
cd "$ROOT/backend"
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload
RUNBACKEND
chmod +x run-backend.sh

cat > run-frontend.sh <<RUNFRONTEND
#!/usr/bin/env bash
set -Eeuo pipefail
cd "$ROOT/frontend"
npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT"
RUNFRONTEND
chmod +x run-frontend.sh

cat > healthcheck-zdash.sh <<HEALTH
#!/usr/bin/env bash
set -Eeuo pipefail

echo "IP:"
hostname -I || true

echo
echo "Ports:"
ss -lntp | grep -E ':$BACKEND_PORT|:$FRONTEND_PORT' || true

echo
echo "Backend health:"
curl -fsS "http://127.0.0.1:$BACKEND_PORT/health" || true

echo
echo "Frontend:"
curl -I "http://127.0.0.1:$FRONTEND_PORT" || true
HEALTH
chmod +x healthcheck-zdash.sh

log "Final git status"
git status --short || true

VM_IP="$(hostname -I | awk '{print $1}')"

cat <<DONE

============================================================
zDash full-stack install complete
============================================================

Repo:
  $ROOT

Backend:
  cd $ROOT
  ./run-backend.sh

Frontend:
  cd $ROOT
  ./run-frontend.sh

Healthcheck:
  cd $ROOT
  ./healthcheck-zdash.sh

Open from Windows/browser:
  http://$VM_IP:$FRONTEND_PORT

Backend health:
  http://$VM_IP:$BACKEND_PORT/health

Useful validation:
  cd $ROOT/backend && source .venv/bin/activate && python -B -m pytest -q
  cd $ROOT/frontend && npm test && npm run build

Optional Docker validation:
  RUN_DOCKER_BUILDS=true bash install-zdash-fullstack.sh

Optional git pull when clean:
  DO_PULL=true bash install-zdash-fullstack.sh

============================================================
DONE

if [ "$START_SERVICES" = "true" ]; then
  log "Starting backend and frontend with nohup"
  cd "$ROOT"
  nohup ./run-backend.sh > backend.log 2>&1 &
  nohup ./run-frontend.sh > frontend.log 2>&1 &
  sleep 3
  ./healthcheck-zdash.sh || true
fi
