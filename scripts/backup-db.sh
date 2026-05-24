#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${BACKUP_DIR:-./backups/db}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUT_DIR"

DB_URL="${DATABASE_URL:-sqlite:///./backend/zdash.db}"

if [[ "$DB_URL" == postgresql* ]]; then
  FILE="$OUT_DIR/zdash-postgres-$TS.sql.gz"
  pg_dump "$DB_URL" | gzip > "$FILE"
  echo "PostgreSQL backup created: $FILE"
else
  SQLITE_PATH="${SQLITE_PATH:-${DB_URL#sqlite:///}}"
  if [[ ! -f "$SQLITE_PATH" ]]; then
    echo "SQLite database file not found: $SQLITE_PATH"
    exit 1
  fi
  FILE="$OUT_DIR/zdash-sqlite-$TS.db"
  cp "$SQLITE_PATH" "$FILE"
  echo "SQLite backup created: $FILE"
fi

find "$OUT_DIR" -type f -mtime +"$RETENTION_DAYS" -delete
