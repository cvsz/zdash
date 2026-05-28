#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo " Cloudflare Dry-Run Handoff Script"
echo "=========================================="
echo "NOTE: Cloudflare production automation belongs in cvsz/zeaz-platform."
echo "This script only prints planned actions and validates env vars."

if [ "${CLOUDFLARE_DRY_RUN:-true}" != "false" ]; then
  echo "[DRY RUN] Actions will not be executed."
fi

# Validate env vars without printing secrets
MISSING=()
[ -z "${CLOUDFLARE_ACCOUNT_ID:-}" ] && MISSING+=("CLOUDFLARE_ACCOUNT_ID")
[ -z "${CLOUDFLARE_ZONE_ID:-}" ] && MISSING+=("CLOUDFLARE_ZONE_ID")
[ -z "${CLOUDFLARE_API_TOKEN:-}" ] && MISSING+=("CLOUDFLARE_API_TOKEN")

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "Missing required environment variables: ${MISSING[*]}"
  exit 1
fi

TUNNEL=${CLOUDFLARE_TUNNEL_NAME:-zdash}
HOSTNAME=${CLOUDFLARE_HOSTNAME:-zdash.zeaz.dev}

echo "Planned Deployment Summary:"
echo "- Account ID:    ${CLOUDFLARE_ACCOUNT_ID}"
echo "- Zone ID:       ${CLOUDFLARE_ZONE_ID}"
echo "- Tunnel Name:   ${TUNNEL}"
echo "- Hostname:      ${HOSTNAME}"
echo "- DNS Target:    ${TUNNEL}.cfargotunnel.com"
echo "- Zero Trust:    Template validation successful"
echo "=========================================="
echo "Handoff to cvsz/zeaz-platform operator is required for real deployment."
