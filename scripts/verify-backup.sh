#!/usr/bin/env bash
set -euo pipefail

BACKUP_FILE="${1:-}"
if [[ -z "$BACKUP_FILE" || ! -f "$BACKUP_FILE" ]]; then
  echo "Usage: $0 <backup-file>"
  exit 1
fi

if [[ "$BACKUP_FILE" == *.tar.gz || "$BACKUP_FILE" == *.tgz ]]; then
  tar -tzf "$BACKUP_FILE" >/dev/null
  echo "Archive integrity OK"
elif [[ "$BACKUP_FILE" == *.gz ]]; then
  gunzip -t "$BACKUP_FILE"
  echo "Gzip integrity OK"
else
  ls -lh "$BACKUP_FILE" >/dev/null
  echo "File exists and is readable"
fi
