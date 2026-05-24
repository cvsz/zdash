#!/usr/bin/env bash
set -euo pipefail

BACKUP_FILE="${1:-}"
if [[ -z "$BACKUP_FILE" || ! -f "$BACKUP_FILE" ]]; then
  echo "Usage: $0 <backup-file>"
  exit 1
fi

read -r -p "Type RESTORE to confirm database restore: " CONFIRM
if [[ "$CONFIRM" != "RESTORE" ]]; then
  echo "Restore aborted"
  exit 1
fi

DB_URL="${DATABASE_URL:-sqlite:///./backend/zdash.db}"

if [[ "$DB_URL" == postgresql* ]]; then
  if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | psql "$DB_URL"
  else
    psql "$DB_URL" < "$BACKUP_FILE"
  fi
  echo "PostgreSQL restore completed"
else
  SQLITE_PATH="${SQLITE_PATH:-${DB_URL#sqlite:///}}"
  cp "$BACKUP_FILE" "$SQLITE_PATH"
  echo "SQLite restore completed"
fi
