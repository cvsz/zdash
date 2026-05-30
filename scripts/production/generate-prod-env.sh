#!/usr/bin/env bash
set -Eeuo pipefail

OUTPUT_FILE="${1:-.env.production}"

if [ -f "$OUTPUT_FILE" ]; then
  echo "ERROR: $OUTPUT_FILE already exists. Remove it first or specify a different path." >&2
  exit 1
fi

JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
BOOTSTRAP_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")
DEFAULT_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")
POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")
API_PEPPER=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")

cat > "$OUTPUT_FILE" << ENVEOF
APP_ENV=production
BACKEND_PORT=8005

POSTGRES_USER=zdash
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=zdash
DATABASE_URL=postgresql+psycopg://zdash:${POSTGRES_PASSWORD}@postgres:5432/zdash

REDIS_URL=redis://redis:6379/0

JWT_SECRET_KEY=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

BOOTSTRAP_ADMIN_USERNAME=admin
BOOTSTRAP_ADMIN_PASSWORD=${BOOTSTRAP_PASSWORD}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_PASSWORD}
API_KEY_HASH_PEPPER=${API_PEPPER}

AUTH_ENABLED=true
PRODUCTION_SAFETY_LOCK=true
PRODUCTION_ALLOW_LIVE_ACTIONS=false
DRY_RUN=true
LIVE_TRADING_ACK=false

RISK_GUARDIAN_ENABLED=true
MT5_ENABLED=false

SOCIAL_DRY_RUN=true
SOCIAL_APPROVAL_REQUIRED=true
SOCIAL_AUTO_POST_ENABLED=false

IOT_DRY_RUN=true
IOT_REQUIRE_CONFIRMATION=true

ALLOW_STRATEGY_PROMOTION=false
UPDATE_DRY_RUN=true

METRICS_AUTH_REQUIRED=true
METRICS_ALLOW_UNAUTHENTICATED_DEV=false

CLAUDE_API_KEY=
CLAUDE_MODEL=claude-sonnet-4-5
OPENAI_API_KEY=
ENVEOF

chmod 600 "$OUTPUT_FILE"
echo "Generated $OUTPUT_FILE with random secrets (chmod 600)"
echo "WARNING: Review and rotate secrets before production use."
echo "WARNING: Never commit $OUTPUT_FILE to version control."
