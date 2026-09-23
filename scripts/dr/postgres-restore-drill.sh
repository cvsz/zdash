#!/usr/bin/env bash
set -Eeuo pipefail

# This drill ONLY operates against an ephemeral local PostgreSQL CI service.
# A production database or remote hostname is never an acceptable target.
if [[ "$DR_TEST_MODE" != "isolated-ci" ]]; then
  echo "BLOCKED: DR_TEST_MODE must be isolated-ci." >&2
  exit 2
fi
if [[ "$PGHOST" != "127.0.0.1" && "$PGHOST" != "localhost" ]]; then
  echo "BLOCKED: the isolated DR drill requires a loopback PostgreSQL host." >&2
  exit 2
fi
if [[ -z "$PGPASSWORD" ]]; then
  echo "BLOCKED: an isolated CI PostgreSQL password is required." >&2
  exit 2
fi

export PGCONNECT_TIMEOUT=5
src_db="zdash_dr_src_$$_$RANDOM"
restore_db="zdash_dr_restore_$$_$RANDOM"
backup_dir="$(mktemp -d)"
backup_file="$backup_dir/zdash-dr.dump"

cleanup() {
  result=$?
  dropdb --if-exists --maintenance-db=postgres "$restore_db" >/dev/null 2>&1 || true
  dropdb --if-exists --maintenance-db=postgres "$src_db" >/dev/null 2>&1 || true
  rm -rf -- "$backup_dir"
  exit "$result"
}
trap cleanup EXIT

pg_isready -q
createdb --maintenance-db=postgres "$src_db"
createdb --maintenance-db=postgres "$restore_db"

# Apply the same canonical migrations used by the PostgreSQL E2E job.
(
  cd backend
  export DATABASE_URL="postgresql+psycopg://$PGUSER:$PGPASSWORD@$PGHOST:$PGPORT/$src_db"
  alembic -c alembic.ini upgrade head
)

# PII-free representative durable fixtures; never copy customer data into CI.
psql -X -v ON_ERROR_STOP=1 --dbname="$src_db" -q <<'SQL'
CREATE TABLE dr_restore_marker (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
INSERT INTO dr_restore_marker (id, payload) VALUES
  ('auth-fixture', 'synthetic-session-record'),
  ('billing-fixture', 'synthetic-ledger-record');
SQL

source_migration="$(psql -X -v ON_ERROR_STOP=1 --dbname="$src_db" -At -c 'SELECT string_agg(version_num, chr(44) ORDER BY version_num) FROM alembic_version')"
source_markers="$(psql -X -v ON_ERROR_STOP=1 --dbname="$src_db" -At -c "SELECT string_agg(id || ':' || payload, ',' ORDER BY id) FROM dr_restore_marker")"
if [[ -z "$source_migration" || -z "$source_markers" ]]; then
  echo "FAIL: source migration or synthetic fixtures missing." >&2
  exit 1
fi

pg_dump --format=custom --no-owner --no-privileges --file="$backup_file" "$src_db"
test -s "$backup_file"
pg_restore --list "$backup_file" >/dev/null
pg_restore --exit-on-error --no-owner --no-privileges --dbname="$restore_db" "$backup_file"

restored_migration="$(psql -X -v ON_ERROR_STOP=1 --dbname="$restore_db" -At -c 'SELECT string_agg(version_num, chr(44) ORDER BY version_num) FROM alembic_version')"
restored_markers="$(psql -X -v ON_ERROR_STOP=1 --dbname="$restore_db" -At -c "SELECT string_agg(id || ':' || payload, ',' ORDER BY id) FROM dr_restore_marker")"

if [[ "$source_migration" != "$restored_migration" || "$source_markers" != "$restored_markers" ]]; then
  echo "FAIL: isolated restore differs from its source database." >&2
  exit 1
fi

# Re-applying all migrations after restore tests schema/application compatibility.
(
  cd backend
  export DATABASE_URL="postgresql+psycopg://$PGUSER:$PGPASSWORD@$PGHOST:$PGPORT/$restore_db"
  alembic -c alembic.ini upgrade head
)

after_migration="$(psql -X -v ON_ERROR_STOP=1 --dbname="$restore_db" -At -c 'SELECT string_agg(version_num, chr(44) ORDER BY version_num) FROM alembic_version')"
if [[ "$after_migration" != "$source_migration" ]]; then
  echo "FAIL: migration replay changed the restored schema revision." >&2
  exit 1
fi

echo "PASS: isolated PostgreSQL dump, restore, synthetic-data comparison and migration replay."
echo "Evidence: $(date -u +%Y-%m-%dT%H:%M:%SZ), source and restore revision $restored_migration"
echo "Dump SHA256: $(sha256sum "$backup_file" | cut -d ' ' -f1)"
echo "This CI drill does not verify target-host backups, RPO, RTO, HA or production recovery."
