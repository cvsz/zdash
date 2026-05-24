#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${BACKUP_DIR:-./backups/config}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
ALLOW_SECRETS="${ALLOW_SECRETS:-false}"
mkdir -p "$OUT_DIR"

FILE="$OUT_DIR/config-$TS.tar.gz"
TMP_DIR="$(mktemp -d)"

cp README.md "$TMP_DIR"/README.md
cp docker-compose.yml "$TMP_DIR"/docker-compose.yml
cp .env.example "$TMP_DIR"/.env.example
cp .env.production.example "$TMP_DIR"/.env.production.example

if [[ "$ALLOW_SECRETS" == "true" ]]; then
  find . -maxdepth 2 -name '.env*' -type f -not -name '.env.example' -not -name '.env.production.example' -exec cp {} "$TMP_DIR"/ \;
fi

tar -czf "$FILE" -C "$TMP_DIR" .
rm -rf "$TMP_DIR"
echo "Config backup created: $FILE"
