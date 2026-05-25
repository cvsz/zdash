#!/usr/bin/env bash
set -euo pipefail
file=${1:-}
[ "${RESTORE_CONFIRM:-no}" = "yes" ] || { echo 'Set RESTORE_CONFIRM=yes'; exit 1; }
[ -f "$file" ] || { echo 'backup file missing'; exit 1; }
gunzip -c "$file" | PGPASSWORD="${POSTGRES_PASSWORD:-}" psql -h "${POSTGRES_HOST:-localhost}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-zdash}" "${POSTGRES_DB:-zdash}"
