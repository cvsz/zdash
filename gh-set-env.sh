# =============================================================================
# GitHub Environment Secrets Bootstrap
# =============================================================================
# REQUIREMENTS:
# - gh auth login
# - repository admin access
# - GitHub Actions enabled
#
# VERIFY:
# gh auth status
# =============================================================================

set -Eeuo pipefail

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------

readonly GH_OWNER="cvsz"
readonly GH_REPO="zdash"
readonly GH_ENV="prod"

readonly REPO="${GH_OWNER}/${GH_REPO}"

# -----------------------------------------------------------------------------
# CREATE ENVIRONMENT
# -----------------------------------------------------------------------------

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${REPO}/environments/${GH_ENV}"

# -----------------------------------------------------------------------------
# NON-SECRET ENVIRONMENT VARIABLES
# -----------------------------------------------------------------------------
# Use GitHub Environment Variables for non-sensitive values.
# Avoid storing plaintext config as secrets unnecessarily.
# -----------------------------------------------------------------------------

gh variable set PRIMARY_DOMAIN \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "zeaz.dev"

gh variable set CLOUDFLARE_PLAN_TIER \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "Free"

gh variable set COST_LOCK \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "true"

gh variable set ALLOW_PAID_CLOUDFLARE_FEATURES \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "false"

gh variable set ALLOW_R2_WRITE \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "false"

gh variable set ALLOW_WORKERS_DEPLOY \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "false"

gh variable set ALLOW_LOAD_BALANCING \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "false"

gh variable set ALLOW_ADVANCED_WAF \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "false"

gh variable set ALLOW_LOGPUSH \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "false"

gh variable set ENVIRONMENT \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "dev"

gh variable set REGION \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "ap-southeast-1"

gh variable set ORIGIN_INFRA_TYPE \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "vm"

gh variable set ORIGIN_HOSTS \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "app.internal,pay.internal"

gh variable set TERRAFORM_BACKEND_TYPE \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "local"

gh variable set TERRAFORM_STATE_BUCKET \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body ""

gh variable set TERRAFORM_LOCK_TABLE \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body ""

gh variable set SECRET_ROTATION_INTERVAL \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "30d"

gh variable set CLOUDFLARE_AI_GATEWAY_SLUG \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "zeaz"

# -----------------------------------------------------------------------------
# SENSITIVE SECRETS
# -----------------------------------------------------------------------------
# BEST PRACTICE:
# - Use scoped API tokens only
# - Never use Global API Key
# - Prefer least privilege tokens
# -----------------------------------------------------------------------------

read -rsp "CLOUDFLARE_ACCOUNT_ID: " CLOUDFLARE_ACCOUNT_ID
echo

gh secret set CLOUDFLARE_ACCOUNT_ID \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "${CLOUDFLARE_ACCOUNT_ID}"

read -rsp "CLOUDFLARE_ZONE_ID: " CLOUDFLARE_ZONE_ID
echo

gh secret set CLOUDFLARE_ZONE_ID \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "${CLOUDFLARE_ZONE_ID}"

read -rsp "CLOUDFLARE_BOOTSTRAP_TOKEN: " CLOUDFLARE_BOOTSTRAP_TOKEN
echo

gh secret set CLOUDFLARE_BOOTSTRAP_TOKEN \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "${CLOUDFLARE_BOOTSTRAP_TOKEN}"

read -rsp "CLOUDFLARE_API_TOKEN: " CLOUDFLARE_API_TOKEN
echo

gh secret set CLOUDFLARE_API_TOKEN \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "${CLOUDFLARE_API_TOKEN}"

read -rsp "CLOUDFLARE_DNS_TOKEN: " CLOUDFLARE_DNS_TOKEN
echo

gh secret set CLOUDFLARE_DNS_TOKEN \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "${CLOUDFLARE_DNS_TOKEN}"

read -rsp "CLOUDFLARE_ZT_TOKEN: " CLOUDFLARE_ZT_TOKEN
echo

gh secret set CLOUDFLARE_ZT_TOKEN \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "${CLOUDFLARE_ZT_TOKEN}"

read -rsp "CLOUDFLARE_WORKERS_TOKEN: " CLOUDFLARE_WORKERS_TOKEN
echo

gh secret set CLOUDFLARE_WORKERS_TOKEN \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "${CLOUDFLARE_WORKERS_TOKEN}"

read -rsp "CLOUDFLARE_PAGES_TOKEN: " CLOUDFLARE_PAGES_TOKEN
echo

gh secret set CLOUDFLARE_PAGES_TOKEN \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "${CLOUDFLARE_PAGES_TOKEN}"

read -rsp "CLOUDFLARE_WAF_TOKEN: " CLOUDFLARE_WAF_TOKEN
echo

gh secret set CLOUDFLARE_WAF_TOKEN \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "${CLOUDFLARE_WAF_TOKEN}"

read -rsp "CLOUDFLARE_TUNNEL_TOKEN: " CLOUDFLARE_TUNNEL_TOKEN
echo

gh secret set CLOUDFLARE_TUNNEL_TOKEN \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "${CLOUDFLARE_TUNNEL_TOKEN}"

read -rsp "CLOUDFLARE_R2_TOKEN: " CLOUDFLARE_R2_TOKEN
echo

gh secret set CLOUDFLARE_R2_TOKEN \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "${CLOUDFLARE_R2_TOKEN}"

read -rsp "CLOUDFLARE_D1_TOKEN: " CLOUDFLARE_D1_TOKEN
echo

gh secret set CLOUDFLARE_D1_TOKEN \
  --env "${GH_ENV}" \
  --repo "${REPO}" \
  --body "${CLOUDFLARE_D1_TOKEN}"

# -----------------------------------------------------------------------------
# VERIFY
# -----------------------------------------------------------------------------

echo
echo "Environment variables:"
gh variable list \
  --env "${GH_ENV}" \
  --repo "${REPO}"

echo
echo "Environment secrets:"
gh secret list \
  --env "${GH_ENV}" \
  --repo "${REPO}"

echo
echo "Bootstrap completed successfully."
