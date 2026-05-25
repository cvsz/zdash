#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
ts=$(date +%Y%m%d-%H%M%S)
out="backups/zdash-${ts}.sql.gz"
PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_dump -h "${POSTGRES_HOST:-localhost}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-zdash}" "${POSTGRES_DB:-zdash}" | gzip > "$out"
find backups -name '*.sql.gz' -mtime +"${RETENTION_DAYS:-7}" -delete
echo "$out"
