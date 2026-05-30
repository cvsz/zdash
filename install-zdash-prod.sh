#!/usr/bin/env bash
set -Eeuo pipefail

# ============================================================
# zDash Production Installer / Updater / Validator
# Repo: https://github.com/cvsz/zdash.git
# Target: Ubuntu 22.04 / 24.04 server or VMware VM
#
# Design goals:
# - production-grade local deployment baseline
# - no paid cloud dependency by default
# - Docker Compose stack: Postgres, Redis, Backend, Frontend, NGINX
# - systemd service, healthcheck, backup, update helpers
# - strict zDash safety lock: dry-run only, no live trading, no live infra mutation
# ============================================================

APP_NAME="${APP_NAME:-zdash}"
REPO_URL="${REPO_URL:-https://github.com/cvsz/zdash.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"

INSTALL_ROOT="${INSTALL_ROOT:-/opt/zdash}"
APP_DIR="${APP_DIR:-$INSTALL_ROOT/app}"
RUNTIME_DIR="${RUNTIME_DIR:-$INSTALL_ROOT/runtime}"
BACKUP_DIR="${BACKUP_DIR:-$INSTALL_ROOT/backups}"
LOG_DIR="${LOG_DIR:-$INSTALL_ROOT/logs}"

ZDASH_DOMAIN="${ZDASH_DOMAIN:-localhost}"
ZDASH_PUBLIC_URL="${ZDASH_PUBLIC_URL:-https://$ZDASH_DOMAIN}"
ZDASH_EMAIL="${ZDASH_EMAIL:-admin@example.local}"

HTTP_PORT="${HTTP_PORT:-80}"
HTTPS_PORT="${HTTPS_PORT:-443}"
BACKEND_PORT="${BACKEND_PORT:-8005}"
FRONTEND_INTERNAL_PORT="${FRONTEND_INTERNAL_PORT:-80}"

POSTGRES_DB="${POSTGRES_DB:-zdash}"
POSTGRES_USER="${POSTGRES_USER:-zdash}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"
JWT_SECRET_KEY="${JWT_SECRET_KEY:-}"
BOOTSTRAP_ADMIN_USERNAME="${BOOTSTRAP_ADMIN_USERNAME:-admin}"
BOOTSTRAP_ADMIN_PASSWORD="${BOOTSTRAP_ADMIN_PASSWORD:-}"

RUN_TESTS="${RUN_TESTS:-false}"
RUN_FRONTEND_TESTS="${RUN_FRONTEND_TESTS:-false}"
ENABLE_UFW="${ENABLE_UFW:-true}"
FORCE_REBUILD="${FORCE_REBUILD:-true}"
SKIP_PULL="${SKIP_PULL:-false}"
INSTALL_DOCKER="${INSTALL_DOCKER:-true}"

ENV_FILE="$RUNTIME_DIR/.env.production"
COMPOSE_FILE="$RUNTIME_DIR/docker-compose.yml"
NGINX_CONF="$RUNTIME_DIR/nginx/zdash.conf"
CERT_DIR="$RUNTIME_DIR/certs"

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

need_root() {
  if [ "${EUID:-$(id -u)}" -ne 0 ]; then
    die "Run as root: sudo $0"
  fi
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1
}

secret_hex() {
  openssl rand -hex 32
}

apt_install() {
  DEBIAN_FRONTEND=noninteractive apt-get install -y "$@"
}

preflight() {
  log "Running preflight checks"

  if ! grep -qiE 'ubuntu|debian' /etc/os-release; then
    warn "This installer is tested on Ubuntu/Debian only. Continuing best-effort."
  fi

  local mem_mb disk_mb
  mem_mb="$(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo)"
  disk_mb="$(df -Pm / | awk 'NR==2 {print $4}')"

  if [ "$mem_mb" -lt 2048 ]; then
    warn "Low memory detected: ${mem_mb}MB. Recommended: 4GB+."
  fi

  if [ "$disk_mb" -lt 10240 ]; then
    warn "Low free disk detected: ${disk_mb}MB. Recommended: 20GB+."
  fi
}

install_packages() {
  log "Installing base packages"
  apt-get update
  apt_install \
    ca-certificates \
    curl \
    git \
    jq \
    openssl \
    ufw \
    cron \
    rsync \
    tar \
    gzip \
    lsb-release \
    gnupg \
    python3 \
    python3-venv \
    python3-pip
}

install_docker() {
  if [ "$INSTALL_DOCKER" != "true" ]; then
    log "Skipping Docker install because INSTALL_DOCKER=false"
    return
  fi

  if need_cmd docker && docker compose version >/dev/null 2>&1; then
    log "Docker and Compose already installed"
    systemctl enable --now docker || true
    return
  fi

  log "Installing Docker Engine from Ubuntu packages"
  apt-get update
  apt_install docker.io docker-compose-v2 || apt_install docker.io docker-compose-plugin
  systemctl enable --now docker

  if ! docker compose version >/dev/null 2>&1; then
    die "Docker Compose plugin is not available after installation."
  fi
}

prepare_dirs() {
  log "Preparing runtime directories"
  mkdir -p "$INSTALL_ROOT" "$APP_DIR" "$RUNTIME_DIR" "$BACKUP_DIR" "$LOG_DIR"
  mkdir -p "$RUNTIME_DIR/nginx" "$RUNTIME_DIR/scripts" "$CERT_DIR" "$LOG_DIR/nginx"
}

resolve_source_repo() {
  # When this script is executed from a checked-out cvsz/zdash repo, use that repo.
  # When executed from elsewhere, clone/update /opt/zdash/app.
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  if [ -d "$script_dir/.git" ] && [ -d "$script_dir/backend" ] && [ -d "$script_dir/frontend" ]; then
    APP_DIR="$script_dir"
    log "Using current zDash checkout: $APP_DIR"
    return
  fi

  if [ -d "$APP_DIR/.git" ]; then
    log "Using existing zDash checkout: $APP_DIR"
    return
  fi

  log "Cloning zDash into $APP_DIR"
  rm -rf "$APP_DIR"
  git clone --branch "$REPO_BRANCH" "$REPO_URL" "$APP_DIR"
}

update_repo() {
  if [ "$SKIP_PULL" = "true" ]; then
    log "Skipping git pull because SKIP_PULL=true"
    return
  fi

  if [ ! -d "$APP_DIR/.git" ]; then
    warn "$APP_DIR is not a git repo. Skipping pull."
    return
  fi

  log "Checking repository status"
  git -C "$APP_DIR" status --short || true

  if [ -n "$(git -C "$APP_DIR" status --porcelain)" ]; then
    warn "Working tree has local changes. Skipping pull to avoid overwriting work."
    return
  fi

  log "Updating zDash branch $REPO_BRANCH"
  git -C "$APP_DIR" fetch origin "$REPO_BRANCH"
  git -C "$APP_DIR" checkout "$REPO_BRANCH"
  git -C "$APP_DIR" pull --ff-only origin "$REPO_BRANCH"
}

generate_secrets() {
  log "Generating missing secrets"
  POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-$(secret_hex)}"
  REDIS_PASSWORD="${REDIS_PASSWORD:-$(secret_hex)}"
  JWT_SECRET_KEY="${JWT_SECRET_KEY:-$(secret_hex)}"
  BOOTSTRAP_ADMIN_PASSWORD="${BOOTSTRAP_ADMIN_PASSWORD:-$(secret_hex)}"
}

write_env() {
  log "Writing production environment file: $ENV_FILE"

  cat > "$ENV_FILE" <<EOF
APP_NAME=zDash
APP_ENV=production
LOG_LEVEL=INFO

BACKEND_HOST=0.0.0.0
BACKEND_PORT=$BACKEND_PORT

DATABASE_URL=postgresql+psycopg://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/$POSTGRES_DB
DB_ECHO=false
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

PRODUCTION_SAFETY_LOCK=true
PRODUCTION_ALLOW_LIVE_ACTIONS=false

AUTH_ENABLED=true
AUTH_ALLOW_BOOTSTRAP_IN_PRODUCTION=true
METRICS_AUTH_REQUIRED=true
METRICS_ALLOW_UNAUTHENTICATED_DEV=false

JWT_SECRET_KEY=$JWT_SECRET_KEY
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

BOOTSTRAP_ADMIN_USERNAME=$BOOTSTRAP_ADMIN_USERNAME
BOOTSTRAP_ADMIN_PASSWORD=$BOOTSTRAP_ADMIN_PASSWORD
DEFAULT_ADMIN_PASSWORD=$BOOTSTRAP_ADMIN_PASSWORD

CLAUDE_API_KEY=
CLAUDE_MODEL=claude-sonnet-4-5
AI_PROVIDER=mock

TRADING_ENABLED=true
DRY_RUN=true
LIVE_TRADING_ACK=false
MT5_ENABLED=false
MT5_LOGIN=
MT5_PASSWORD=
MT5_SERVER=
MT5_PATH=
TRADING_DEFAULT_SYMBOL=XAUUSD
TRADING_DEFAULT_TIMEFRAME=M5
TRADING_DEFAULT_STRATEGY=trend_momentum_v1
TRADING_MAX_SIGNAL_AGE_SECONDS=300
FUNNEL_FAST_PERIOD=21
FUNNEL_MEDIUM_PERIOD=10
FUNNEL_SLOW_PERIOD=3
AI_TRADING_ANALYSIS_ENABLED=true
AI_TRADING_PROVIDER=mock

RISK_GUARDIAN_ENABLED=true
MAX_DAILY_DRAWDOWN_PERCENT=5.0
MAX_TOTAL_DRAWDOWN_PERCENT=20.0
EMERGENCY_KILL_SWITCH_DRAWDOWN_PERCENT=50.0
SOFT_HALT_DRAWDOWN_LEVEL_1=5.0
SOFT_HALT_DRAWDOWN_LEVEL_2=10.0
SOFT_HALT_DRAWDOWN_LEVEL_3=20.0
ALLOW_MANUAL_RESUME=true
REQUIRE_RESUME_REASON=true
HARD_HALT_ON_DAILY_DRAWDOWN=false

SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=Asia/Bangkok
SCHEDULER_DEFAULT_MAX_RUNTIME_SECONDS=300
SCHEDULER_ALLOW_MANUAL_RUN=true
SCHEDULER_STORE=in_memory
FRIDAY_AGENT_ENABLED=true

CONTENT_PIPELINE_ENABLED=true
CONTENT_STORE=in_memory
EDITOR_AGENT_ENABLED=true
GRAPHIC_AGENT_ENABLED=true
SOCIAL_AGENT_ENABLED=true
CONTENT_DEFAULT_BRAND=zDash
CONTENT_DEFAULT_LANGUAGE=en
CONTENT_DEFAULT_TONE=professional
CONTENT_REQUIRE_POLICY_CHECK=true
IMAGE_GENERATION_PROVIDER=mock
IMAGE_DRY_RUN=true
IMAGE_OUTPUT_DIR=backend/data/content/images
SOCIAL_PROVIDER=mock
SOCIAL_DRY_RUN=true
SOCIAL_APPROVAL_REQUIRED=true
SOCIAL_AUTO_POST_ENABLED=false
SOCIAL_REAL_POSTING_APPROVED=false
SOCIAL_DEFAULT_PLATFORMS=x,tiktok,facebook,instagram,linkedin

IOT_ENABLED=true
IOT_DRY_RUN=true
IOT_REQUIRE_CONFIRMATION=true
IOT_REAL_ACTIONS_APPROVED=false
TAPO_USERNAME=
TAPO_PASSWORD=
TAPO_DEVICE_IP=
TAPO_DEVICE_ALIAS=zdash-power-node

MULTI_TENANT_ENABLED=true
DEFAULT_ORG_NAME=zDash Production
DEFAULT_WORKSPACE_NAME=Main Workspace
TENANT_HEADER_NAME=X-ZDash-Tenant
WORKSPACE_HEADER_NAME=X-ZDash-Workspace

WORKER_QUEUE_BACKEND=memory
WORKER_MAX_RETRIES=3

CLOUDFLARE_DRY_RUN=true
NOTIFICATION_DRY_RUN=true

POSTGRES_DB=$POSTGRES_DB
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD

ZDASH_DOMAIN=$ZDASH_DOMAIN
ZDASH_PUBLIC_URL=$ZDASH_PUBLIC_URL
EOF

  chmod 600 "$ENV_FILE"
}

write_nginx_conf() {
  log "Writing reverse proxy config: $NGINX_CONF"

  cat > "$NGINX_CONF" <<EOF
server {
  listen 80;
  server_name $ZDASH_DOMAIN;

  location / {
    return 301 https://\$host\$request_uri;
  }

  location = /health {
    access_log off;
    return 200 "ok\n";
  }
}

server {
  listen 443 ssl http2;
  server_name $ZDASH_DOMAIN;

  ssl_certificate /etc/nginx/certs/fullchain.pem;
  ssl_certificate_key /etc/nginx/certs/privkey.pem;
  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_session_cache shared:SSL:10m;
  ssl_session_timeout 10m;

  client_max_body_size 50m;

  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
  add_header X-Content-Type-Options nosniff always;
  add_header X-Frame-Options SAMEORIGIN always;
  add_header Referrer-Policy strict-origin-when-cross-origin always;
  add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

  gzip on;
  gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;

  location /api/ {
    proxy_pass http://backend:8005/api/;
    proxy_http_version 1.1;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;
    proxy_read_timeout 120s;
  }

  location /metrics {
    proxy_pass http://backend:8005/metrics;
    proxy_http_version 1.1;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;
  }

  location /ws {
    proxy_pass http://backend:8005/ws;
    proxy_http_version 1.1;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host \$host;
    proxy_read_timeout 3600s;
  }

  location / {
    proxy_pass http://frontend:80;
    proxy_http_version 1.1;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;
  }

  location = /health {
    access_log off;
    return 200 "ok\n";
  }
}
EOF
}

generate_cert() {
  log "Ensuring TLS certificate exists"

  if [ -s "$CERT_DIR/fullchain.pem" ] && [ -s "$CERT_DIR/privkey.pem" ]; then
    echo "Existing certificate found in $CERT_DIR"
    return
  fi

  openssl req -x509 -nodes -newkey rsa:4096 -days 3650 \
    -keyout "$CERT_DIR/privkey.pem" \
    -out "$CERT_DIR/fullchain.pem" \
    -subj "/CN=$ZDASH_DOMAIN" \
    -addext "subjectAltName=DNS:$ZDASH_DOMAIN,DNS:localhost,IP:127.0.0.1"

  chmod 600 "$CERT_DIR/privkey.pem"
}

write_compose() {
  log "Writing Docker Compose file: $COMPOSE_FILE"

  cat > "$COMPOSE_FILE" <<EOF
services:
  postgres:
    image: postgres:16-alpine
    container_name: zdash-postgres
    restart: unless-stopped
    env_file:
      - $ENV_FILE
    environment:
      POSTGRES_DB: \${POSTGRES_DB}
      POSTGRES_USER: \${POSTGRES_USER}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - zdash_internal
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \${POSTGRES_USER} -d \${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    container_name: zdash-redis
    restart: unless-stopped
    env_file:
      - $ENV_FILE
    command: ["sh", "-c", "redis-server --appendonly yes --requirepass \"\$REDIS_PASSWORD\""]
    volumes:
      - redis_data:/data
    networks:
      - zdash_internal
    healthcheck:
      test: ["CMD-SHELL", "redis-cli -a \"\$REDIS_PASSWORD\" ping | grep PONG"]
      interval: 10s
      timeout: 5s
      retries: 10

  backend:
    build:
      context: $APP_DIR
      dockerfile: infra/docker/backend.Dockerfile
    container_name: zdash-backend
    restart: unless-stopped
    env_file:
      - $ENV_FILE
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    expose:
      - "8005"
    volumes:
      - backend_data:/app/backend/data
      - $LOG_DIR:/app/backend/logs
    networks:
      - zdash_internal
    healthcheck:
      test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:8005/health')\" || exit 1"]
      interval: 30s
      timeout: 10s
      start_period: 45s
      retries: 10

  frontend:
    build:
      context: $APP_DIR
      dockerfile: infra/docker/frontend.Dockerfile
    container_name: zdash-frontend
    restart: unless-stopped
    depends_on:
      backend:
        condition: service_healthy
    expose:
      - "80"
    networks:
      - zdash_internal
    healthcheck:
      test: ["CMD-SHELL", "wget -q -O - http://127.0.0.1/ >/dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      start_period: 20s
      retries: 10

  nginx:
    image: nginx:1.27-alpine
    container_name: zdash-nginx
    restart: unless-stopped
    depends_on:
      frontend:
        condition: service_healthy
      backend:
        condition: service_healthy
    ports:
      - "$HTTP_PORT:80"
      - "$HTTPS_PORT:443"
    volumes:
      - $NGINX_CONF:/etc/nginx/conf.d/default.conf:ro
      - $CERT_DIR:/etc/nginx/certs:ro
      - $LOG_DIR/nginx:/var/log/nginx
    networks:
      - zdash_public
      - zdash_internal
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- --no-check-certificate https://127.0.0.1/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 10

networks:
  zdash_public:
    driver: bridge
  zdash_internal:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  backend_data:
EOF
}

run_backend_tests() {
  if [ "$RUN_TESTS" != "true" ]; then
    log "Skipping backend tests because RUN_TESTS=false"
    return
  fi

  log "Running backend lint/tests"
  cd "$APP_DIR/backend"
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install --upgrade pip setuptools wheel
  python -m pip install -e '.[dev]'
  python -m ruff check app tests
  python -B -m pytest -q
  deactivate
}

run_frontend_tests() {
  if [ "$RUN_FRONTEND_TESTS" != "true" ]; then
    log "Skipping frontend host tests because RUN_FRONTEND_TESTS=false"
    return
  fi

  if ! need_cmd npm; then
    warn "npm not found. Skipping frontend host tests. Docker build will still compile frontend."
    return
  fi

  log "Running frontend tests/build on host"
  cd "$APP_DIR/frontend"
  npm install --legacy-peer-deps --no-audit --fund=false
  npm test
  npm run build
}

dc() {
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

deploy_stack() {
  log "Deploying zDash Docker Compose stack"
  cd "$RUNTIME_DIR"

  if [ "$FORCE_REBUILD" = "true" ]; then
    dc build --pull
  fi

  dc up -d
}

write_systemd() {
  log "Writing systemd services"

  cat > /etc/systemd/system/zdash.service <<EOF
[Unit]
Description=zDash Production Full Stack
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$RUNTIME_DIR
ExecStart=/usr/bin/docker compose --env-file $ENV_FILE -f $COMPOSE_FILE up -d
ExecStop=/usr/bin/docker compose --env-file $ENV_FILE -f $COMPOSE_FILE down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

  cat > /etc/systemd/system/zdash-backup.service <<EOF
[Unit]
Description=zDash backup

[Service]
Type=oneshot
ExecStart=$RUNTIME_DIR/scripts/zdash-backup.sh
EOF

  cat > /etc/systemd/system/zdash-backup.timer <<EOF
[Unit]
Description=Run zDash backup daily

[Timer]
OnCalendar=*-*-* 03:15:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

  systemctl daemon-reload
  systemctl enable zdash.service
  systemctl enable --now zdash-backup.timer
}

write_helper_scripts() {
  log "Writing helper scripts"

  cat > "$RUNTIME_DIR/scripts/zdash-health.sh" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail

echo "[\$(date -Is)] Docker services"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps

echo
echo "[\$(date -Is)] Backend health"
docker exec zdash-backend sh -lc "python -c \"import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8005/health').read().decode())\"" || true

echo
echo "[\$(date -Is)] HTTPS health"
curl -kfsS https://127.0.0.1/health || true

echo
echo "[\$(date -Is)] Recent backend logs"
docker logs --tail=100 zdash-backend || true
EOF
  chmod +x "$RUNTIME_DIR/scripts/zdash-health.sh"

  cat > "$RUNTIME_DIR/scripts/zdash-logs.sh" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail
service="\${1:-}"
if [ -n "\$service" ]; then
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs -f --tail=200 "\$service"
else
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs -f --tail=200
fi
EOF
  chmod +x "$RUNTIME_DIR/scripts/zdash-logs.sh"

  cat > "$RUNTIME_DIR/scripts/zdash-update.sh" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail

cd "$APP_DIR"
if [ -z "\$(git status --porcelain)" ]; then
  git fetch origin "$REPO_BRANCH"
  git checkout "$REPO_BRANCH"
  git pull --ff-only origin "$REPO_BRANCH"
else
  echo "Working tree has local changes; skipping git pull."
fi

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build --pull
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d
"$RUNTIME_DIR/scripts/zdash-health.sh"
EOF
  chmod +x "$RUNTIME_DIR/scripts/zdash-update.sh"

  cat > "$RUNTIME_DIR/scripts/zdash-backup.sh" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail

stamp="\$(date +%Y%m%d-%H%M%S)"
out_dir="$BACKUP_DIR/zdash-\$stamp"
mkdir -p "\$out_dir"

echo "[\$(date -Is)] Backup started: \$out_dir"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "\$out_dir/postgres.sql.gz"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config > "\$out_dir/docker-compose.rendered.yml"
sha256sum "$ENV_FILE" > "\$out_dir/env.sha256"

tar -czf "\$out_dir.tar.gz" -C "$BACKUP_DIR" "zdash-\$stamp"
rm -rf "\$out_dir"
find "$BACKUP_DIR" -name 'zdash-*.tar.gz' -type f -mtime +7 -delete

echo "[\$(date -Is)] Backup completed: \$out_dir.tar.gz"
EOF
  chmod +x "$RUNTIME_DIR/scripts/zdash-backup.sh"
}

configure_firewall() {
  if [ "$ENABLE_UFW" != "true" ]; then
    log "Skipping UFW because ENABLE_UFW=false"
    return
  fi

  log "Configuring UFW"
  ufw allow OpenSSH || true
  ufw allow "$HTTP_PORT/tcp" || true
  ufw allow "$HTTPS_PORT/tcp" || true
  ufw --force enable || true
}

print_summary() {
  local server_ip
  server_ip="$(hostname -I | awk '{print $1}')"

  cat <<EOF

============================================================
zDash production install/update complete
============================================================

Repo:
  $APP_DIR

Runtime:
  $RUNTIME_DIR

Public URL:
  https://$ZDASH_DOMAIN

Local health:
  curl -k https://127.0.0.1/health
  $RUNTIME_DIR/scripts/zdash-health.sh

Server IP:
  https://$server_ip

Admin bootstrap:
  username: $BOOTSTRAP_ADMIN_USERNAME
  password: $BOOTSTRAP_ADMIN_PASSWORD

Safety locks enforced:
  DRY_RUN=true
  LIVE_TRADING_ACK=false
  MT5_ENABLED=false
  PRODUCTION_ALLOW_LIVE_ACTIONS=false
  RISK_GUARDIAN_ENABLED=true
  SOCIAL_DRY_RUN=true
  IOT_DRY_RUN=true
  CLOUDFLARE_DRY_RUN=true

Commands:
  systemctl status zdash
  docker compose --env-file $ENV_FILE -f $COMPOSE_FILE ps
  $RUNTIME_DIR/scripts/zdash-logs.sh backend
  $RUNTIME_DIR/scripts/zdash-backup.sh
  $RUNTIME_DIR/scripts/zdash-update.sh

TLS:
  Self-signed cert is installed by default.
  Replace these files with real certs or route through Cloudflare Tunnel:
    $CERT_DIR/fullchain.pem
    $CERT_DIR/privkey.pem

============================================================

EOF
}

main() {
  need_root
  preflight
  install_packages
  install_docker
  prepare_dirs
  resolve_source_repo
  update_repo
  generate_secrets
  write_env
  write_nginx_conf
  generate_cert
  write_compose
  run_backend_tests
  run_frontend_tests
  deploy_stack
  write_helper_scripts
  write_systemd
  configure_firewall
  print_summary
}

main "$@"
