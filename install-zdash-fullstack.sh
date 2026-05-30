#!/usr/bin/env bash
set -Eeuo pipefail

# ============================================================
# zDash Full-Stack Installer / Repair / Validator
# Target: Ubuntu 22.04/24.04 VM or local Linux workstation
# Repo:   ~/zdash or https://github.com/cvsz/zdash.git
#
# Purpose:
# - local developer setup
# - VMware/LAN dashboard setup
# - safe repair after dependency/network issues
# - validation before production installer usage
#
# Safety defaults:
# - dry-run trading only
# - MT5/live broker disabled
# - IoT/social/cloud mutation disabled or gated
# - Guardian risk enabled
# ============================================================

ROOT="${ROOT:-$HOME/zdash}"
REPO_URL="${REPO_URL:-https://github.com/cvsz/zdash.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"

BACKEND_PORT="${BACKEND_PORT:-8005}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
NODE_MAJOR="${NODE_MAJOR:-20}"

DO_PULL="${DO_PULL:-false}"
RUN_BACKEND_TESTS="${RUN_BACKEND_TESTS:-true}"
RUN_FRONTEND_TESTS="${RUN_FRONTEND_TESTS:-true}"
RUN_FRONTEND_BUILD="${RUN_FRONTEND_BUILD:-true}"
RUN_DOCKER_BUILDS="${RUN_DOCKER_BUILDS:-false}"
INSTALL_DOCKER="${INSTALL_DOCKER:-false}"
START_SERVICES="${START_SERVICES:-false}"
FORCE_BACKEND_REINSTALL="${FORCE_BACKEND_REINSTALL:-false}"

NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
BACKUP_DIR="${BACKUP_DIR:-$ROOT/.installer-backups}"

log() {
  printf '\n\033[1;36m[%s]\033[0m %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

warn() {
  printf '\n\033[1;33m[WARN]\033[0m %s\n' "$*"
}

die() {
  printf '\n\033[1;31m[ERROR]\033[0m %s\n' "$*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1
}

run_sudo() {
  if [ "${EUID:-$(id -u)}" -eq 0 ]; then
    "$@"
  elif need_cmd sudo; then
    sudo "$@"
  else
    die "Need root privileges for: $*"
  fi
}

apt_install() {
  run_sudo apt-get update
  run_sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "$@"
}

safe_mkdir() {
  mkdir -p "$1"
}

escape_sed_value() {
  printf '%s' "$1" | sed -e 's/[\/&]/\\&/g'
}

upsert_env() {
  local key="$1"
  local value="$2"
  local file="${3:-$ROOT/.env}"
  local escaped
  escaped="$(escape_sed_value "$value")"

  touch "$file"

  if grep -qE "^${key}=" "$file"; then
    sed -i "s/^${key}=.*/${key}=${escaped}/" "$file"
  else
    printf '%s=%s\n' "$key" "$value" >> "$file"
  fi
}

append_section_once() {
  local marker="$1"
  local file="$2"

  if ! grep -qF "$marker" "$file" 2>/dev/null; then
    printf '\n%s\n' "$marker" >> "$file"
  fi
}

preflight() {
  log "zDash full-stack installer starting"

  unset GITHUB_TOKEN || true
  unset GH_TOKEN || true

  local mem_mb disk_mb
  mem_mb="$(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo 2>/dev/null || echo 0)"
  disk_mb="$(df -Pm "${HOME:-/}" | awk 'NR==2 {print $4}' 2>/dev/null || echo 0)"

  if [ "$mem_mb" -gt 0 ] && [ "$mem_mb" -lt 2048 ]; then
    warn "Low memory detected: ${mem_mb}MB. Recommended: 4GB+."
  fi

  if [ "$disk_mb" -gt 0 ] && [ "$disk_mb" -lt 8192 ]; then
    warn "Low free disk detected: ${disk_mb}MB. Recommended: 10GB+."
  fi
}

install_system_packages() {
  log "Installing system packages without apt npm/nodejs"

  apt_install \
    git \
    curl \
    ca-certificates \
    build-essential \
    pkg-config \
    openssl \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    jq \
    rsync \
    iproute2
}

install_docker_if_requested() {
  if [ "$INSTALL_DOCKER" != "true" ] && [ "$RUN_DOCKER_BUILDS" != "true" ]; then
    return
  fi

  log "Ensuring Docker is available"

  if need_cmd docker && docker compose version >/dev/null 2>&1; then
    echo "Docker already available."
    return
  fi

  apt_install docker.io docker-compose-v2 || apt_install docker.io docker-compose-plugin
  run_sudo systemctl enable --now docker || true

  if ! docker compose version >/dev/null 2>&1; then
    die "Docker Compose plugin not available."
  fi
}

install_nvm_node() {
  log "Ensuring nvm + Node ${NODE_MAJOR} LTS"

  export NVM_DIR

  if [ ! -s "$NVM_DIR/nvm.sh" ]; then
    log "Installing nvm into $NVM_DIR"
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
  fi

  # shellcheck disable=SC1091
  source "$NVM_DIR/nvm.sh"

  nvm install "$NODE_MAJOR"
  nvm use "$NODE_MAJOR"
  nvm alias default "$NODE_MAJOR" >/dev/null

  log "Node versions"
  node --version
  npm --version
}

clone_or_use_repo() {
  if [ ! -d "$ROOT/.git" ]; then
    log "Cloning zDash into $ROOT"
    safe_mkdir "$(dirname "$ROOT")"
    git clone --branch "$REPO_BRANCH" "$REPO_URL" "$ROOT"
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
      log "Pulling latest $REPO_BRANCH"
      git fetch origin "$REPO_BRANCH"
      git checkout "$REPO_BRANCH"
      git pull --ff-only origin "$REPO_BRANCH"
    fi
  fi
}

backup_env() {
  if [ -f "$ROOT/.env" ]; then
    safe_mkdir "$BACKUP_DIR"
    cp "$ROOT/.env" "$BACKUP_DIR/.env.$(date +%Y%m%d-%H%M%S).bak"
  fi
}

ensure_env() {
  log "Ensuring safe .env exists"

  cd "$ROOT"

  if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
      cp .env.example .env
    else
      touch .env
    fi
  fi

  backup_env

  append_section_once "# zDash full-stack installer managed safety defaults" ".env"

  upsert_env "APP_NAME" "zDash"
  upsert_env "APP_ENV" "development"
  upsert_env "LOG_LEVEL" "INFO"
  upsert_env "BACKEND_HOST" "0.0.0.0"
  upsert_env "BACKEND_PORT" "$BACKEND_PORT"

  # Local dev should keep SQLite unless the user configures Postgres manually.
  if ! grep -qE '^DATABASE_URL=' .env; then
    upsert_env "DATABASE_URL" "sqlite:///./zdash.db"
  fi

  upsert_env "PRODUCTION_SAFETY_LOCK" "true"
  upsert_env "PRODUCTION_ALLOW_LIVE_ACTIONS" "false"

  upsert_env "AUTH_ENABLED" "false"
  upsert_env "AUTH_ALLOW_BOOTSTRAP_IN_PRODUCTION" "false"
  upsert_env "METRICS_AUTH_REQUIRED" "false"
  upsert_env "METRICS_ALLOW_UNAUTHENTICATED_DEV" "true"

  if ! grep -qE '^JWT_SECRET_KEY=' .env; then
    upsert_env "JWT_SECRET_KEY" "dev-only-change-before-production"
  fi

  upsert_env "AI_PROVIDER" "mock"
  upsert_env "AI_TRADING_PROVIDER" "mock"
  upsert_env "CLAUDE_API_KEY" ""

  upsert_env "TRADING_ENABLED" "true"
  upsert_env "DRY_RUN" "true"
  upsert_env "LIVE_TRADING_ACK" "false"
  upsert_env "MT5_ENABLED" "false"
  upsert_env "TRADING_DEFAULT_SYMBOL" "XAUUSD"
  upsert_env "TRADING_DEFAULT_TIMEFRAME" "M5"
  upsert_env "TRADING_DEFAULT_STRATEGY" "trend_momentum_v1"

  upsert_env "RISK_GUARDIAN_ENABLED" "true"
  upsert_env "MAX_DAILY_DRAWDOWN_PERCENT" "5.0"
  upsert_env "MAX_TOTAL_DRAWDOWN_PERCENT" "20.0"
  upsert_env "EMERGENCY_KILL_SWITCH_DRAWDOWN_PERCENT" "50.0"

  upsert_env "SCHEDULER_ENABLED" "true"
  upsert_env "SCHEDULER_TIMEZONE" "Asia/Bangkok"
  upsert_env "SCHEDULER_STORE" "in_memory"

  upsert_env "CONTENT_PIPELINE_ENABLED" "true"
  upsert_env "CONTENT_STORE" "in_memory"
  upsert_env "CONTENT_REQUIRE_POLICY_CHECK" "true"
  upsert_env "IMAGE_GENERATION_PROVIDER" "mock"
  upsert_env "IMAGE_DRY_RUN" "true"
  upsert_env "SOCIAL_PROVIDER" "mock"
  upsert_env "SOCIAL_DRY_RUN" "true"
  upsert_env "SOCIAL_APPROVAL_REQUIRED" "true"
  upsert_env "SOCIAL_AUTO_POST_ENABLED" "false"
  upsert_env "SOCIAL_REAL_POSTING_APPROVED" "false"

  upsert_env "IOT_ENABLED" "true"
  upsert_env "IOT_DRY_RUN" "true"
  upsert_env "IOT_REQUIRE_CONFIRMATION" "true"
  upsert_env "IOT_REAL_ACTIONS_APPROVED" "false"

  upsert_env "MULTI_TENANT_ENABLED" "false"
  upsert_env "DEFAULT_ORG_NAME" "zDash Local"
  upsert_env "DEFAULT_WORKSPACE_NAME" "Main Workspace"

  upsert_env "WORKER_QUEUE_BACKEND" "memory"
  upsert_env "CLOUDFLARE_DRY_RUN" "true"
  upsert_env "NOTIFICATION_DRY_RUN" "true"
}

setup_backend() {
  log "Backend setup"

  cd "$ROOT/backend"

  if [ "$FORCE_BACKEND_REINSTALL" = "true" ]; then
    rm -rf .venv
  fi

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
  else
    die "No backend pyproject.toml or requirements.txt found."
  fi

  python -m pip install --upgrade ruff pytest pytest-cov httpx

  log "Backend lint check"
  python -m ruff check app tests

  if [ "$RUN_BACKEND_TESTS" = "true" ]; then
    log "Backend tests"
    python -B -m pytest -q
  else
    warn "Skipping backend tests because RUN_BACKEND_TESTS=false"
  fi

  deactivate
}

setup_frontend() {
  log "Frontend setup"

  export NVM_DIR
  # shellcheck disable=SC1091
  source "$NVM_DIR/nvm.sh"
  nvm use "$NODE_MAJOR"

  cd "$ROOT/frontend"

  if [ ! -f ".npmrc" ]; then
    echo "legacy-peer-deps=true" > .npmrc
  fi

  npm install --legacy-peer-deps --no-audit --fund=false

  if [ "$RUN_FRONTEND_TESTS" = "true" ]; then
    log "Frontend tests"
    npm test
  else
    warn "Skipping frontend tests because RUN_FRONTEND_TESTS=false"
  fi

  if [ "$RUN_FRONTEND_BUILD" = "true" ]; then
    log "Frontend production build"
    npm run build
  else
    warn "Skipping frontend build because RUN_FRONTEND_BUILD=false"
  fi
}

run_docker_validation() {
  if [ "$RUN_DOCKER_BUILDS" != "true" ]; then
    return
  fi

  log "Docker validation builds"
  cd "$ROOT"

  docker build -f infra/docker/backend.Dockerfile -t zdash-backend:local .
  docker build -f infra/docker/frontend.Dockerfile -t zdash-frontend:local .
}

write_helper_scripts() {
  log "Creating helper scripts"

  cd "$ROOT"

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
export NVM_DIR="$NVM_DIR"
source "\$NVM_DIR/nvm.sh"
nvm use "$NODE_MAJOR"
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
echo "Backend API health fallback:"
curl -fsS "http://127.0.0.1:$BACKEND_PORT/api/health" || true

echo
echo "Frontend:"
curl -I "http://127.0.0.1:$FRONTEND_PORT" || true
HEALTH
  chmod +x healthcheck-zdash.sh

  cat > validate-zdash.sh <<VALIDATE
#!/usr/bin/env bash
set -Eeuo pipefail
export NVM_DIR="$NVM_DIR"

cd "$ROOT/backend"
source .venv/bin/activate
python -m ruff check app tests
python -B -m pytest -q

deactivate
source "\$NVM_DIR/nvm.sh"
nvm use "$NODE_MAJOR"
cd "$ROOT/frontend"
npm test
npm run build
VALIDATE
  chmod +x validate-zdash.sh

  cat > repair-zdash.sh <<REPAIR
#!/usr/bin/env bash
set -Eeuo pipefail
cd "$ROOT"
FORCE_BACKEND_REINSTALL=true RUN_BACKEND_TESTS=true RUN_FRONTEND_TESTS=true RUN_FRONTEND_BUILD=true bash install-zdash-fullstack.sh
REPAIR
  chmod +x repair-zdash.sh
}

start_services_if_requested() {
  if [ "$START_SERVICES" != "true" ]; then
    return
  fi

  log "Starting backend and frontend with nohup"
  cd "$ROOT"

  pkill -f "uvicorn app.main:app" 2>/dev/null || true
  pkill -f "vite.*--port $FRONTEND_PORT" 2>/dev/null || true

  nohup ./run-backend.sh > backend.log 2>&1 &
  nohup ./run-frontend.sh > frontend.log 2>&1 &
  sleep 5
  ./healthcheck-zdash.sh || true
}

print_summary() {
  cd "$ROOT"

  log "Final git status"
  git status --short || true

  local vm_ip
  vm_ip="$(hostname -I | awk '{print $1}')"

  cat <<DONE

============================================================
zDash full-stack install / repair complete
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

Validate all:
  cd $ROOT
  ./validate-zdash.sh

Repair full setup:
  cd $ROOT
  ./repair-zdash.sh

Open from Windows/browser:
  http://$vm_ip:$FRONTEND_PORT

Backend health:
  http://$vm_ip:$BACKEND_PORT/health

Optional service start:
  START_SERVICES=true bash install-zdash-fullstack.sh

Optional git pull when clean:
  DO_PULL=true bash install-zdash-fullstack.sh

Optional Docker validation:
  RUN_DOCKER_BUILDS=true INSTALL_DOCKER=true bash install-zdash-fullstack.sh

Safety defaults enforced in .env:
  DRY_RUN=true
  LIVE_TRADING_ACK=false
  MT5_ENABLED=false
  PRODUCTION_ALLOW_LIVE_ACTIONS=false
  RISK_GUARDIAN_ENABLED=true
  SOCIAL_DRY_RUN=true
  IOT_DRY_RUN=true
  CLOUDFLARE_DRY_RUN=true

Notes:
  - This installer is for local/dev/VM full-stack use.
  - For Docker/systemd/Postgres/NGINX production baseline, use ./install-zdash-prod.sh.
  - Node is managed through nvm, not Ubuntu apt npm.

============================================================
DONE
}

main() {
  preflight
  install_system_packages
  install_docker_if_requested
  install_nvm_node
  clone_or_use_repo
  ensure_env
  setup_backend
  setup_frontend
  run_docker_validation
  write_helper_scripts
  start_services_if_requested
  print_summary
}

main "$@"
