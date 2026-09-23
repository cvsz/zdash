# PostgreSQL Backup and Restore — Production Acceptance

## 1. CI proof (synthetic, isolated only)

Every pull request runs the `ci / postgres-dr` job. Its local PostgreSQL 16
service is independent from any customer or production database.

The job applies canonical Alembic migrations, inserts PII-free synthetic
fixtures, creates a custom-format `pg_dump`, restores into a **second empty
database**, compares migration revision and durable fixture content, then
replays Alembic migrations. Both disposable databases and the local dump
are removed on exit. A failed dump, restore, comparison or migration fails CI.

Manual reproduction requires a local throwaway PostgreSQL instance, not a
production connection. The script requires `DR_TEST_MODE=isolated-ci` and a
loopback `PGHOST`; use the GitHub Actions job as the reproducible reference.

**Limitation:** CI does not prove the production data can be recovered, does
not establish off-site retention, and does not measure production RPO/RTO.

## 2. Production backup prerequisites

- Rotate previously exposed passwords and use the operator's secret manager.
- Record the target PostgreSQL major version, backup storage location,
  ownership, encryption, retention, integrity checks and alert routing.
- Use the production `infra/scripts/backup-postgres.sh` with the correct
  `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_DB`
  and `POSTGRES_PASSWORD` provided **outside Git and command-line arguments**.
- Run `gzip -t <backup.sql.gz>` and record the file's SHA256; gzip integrity
  alone is **not** restore evidence.
- Store an encrypted off-site copy and validate read-back by an independently
  authorized operator. Exclude database contents and credentials from public
  GitHub artifacts.

## 3. Isolated production-data restore drill

1. Provision a dedicated, access-controlled **disposable** PostgreSQL target
   with the correct major version. It must not expose live services or route
   to customer workflows; record its unique target host and database.
2. Verify that the target is **not** the production PostgreSQL server.
   Export target-specific `POSTGRES_HOST`, `POSTGRES_PORT`,
   `POSTGRES_USER`, `POSTGRES_DB` and a fresh target-only
   `POSTGRES_PASSWORD` from the secret manager.
3. Restore a controlled copy of the production backup. Only after the
   explicit isolated-target check, run:
   ```bash
   RESTORE_CONFIRM=yes bash infra/scripts/restore-postgres.sh /secure/backup.sql.gz
   ```
   Do **not** use this example against the production database. The existing
   restore script is intentionally an operator action, not an automated
   production mutation.
4. Verify Alembic revision and representative **sanitized** business records
   on the isolated target. Run application-level read-only smoke tests and
   check dependency compatibility without sending notifications or orders.
5. Record actual start/end timestamps and observed RPO/RTO. An operator must
   compare measured results with an **approved** recovery objective.
6. Destroy the isolated data securely according to the organization's policy,
   and record an evidence reference without attaching confidential rows.

## 4. Release gates and evidence

A CI PASS and an isolated target-host restore PASS are **different** gates.
Record both with the precise release SHA, image digest, backup identifier,
verification UTC timestamp, tested PostgreSQL version, operator and
redacted evidence location. Separately prove HTTPS, RBAC, alerts and a
rollback using a known-good immutable image. Use
`docs/ops/PRODUCTION_ACCEPTANCE_TEMPLATE.md` for the final operator record.

Never declare production-ready from file existence, command exit status,
a local rehearsal, or a CI-generated synthetic restore alone.
