#!/usr/bin/env bash
set -euo pipefail

# Wrapper to run the canonical ECC global sync from a local ECC checkout.
# Usage:
#   scripts/sync-ecc-to-codex.sh [ECC_SOURCE_PATH] [--update-mcp]

ECC_SOURCE="${1:-/home/zeazdev/ECC}"
shift || true

args=()
for arg in "$@"; do
  case "$arg" in
    --update-mcp) args+=("--update-mcp") ;;
    --dry-run) args+=("--dry-run") ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 1
      ;;
  esac
done

if [[ ! -x "$ECC_SOURCE/scripts/sync-ecc-to-codex.sh" ]]; then
  echo "ECC sync script not found at: $ECC_SOURCE/scripts/sync-ecc-to-codex.sh" >&2
  exit 1
fi

exec "$ECC_SOURCE/scripts/sync-ecc-to-codex.sh" "${args[@]}"
