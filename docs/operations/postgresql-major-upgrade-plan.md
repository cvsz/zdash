# PostgreSQL major upgrade plan

## Current baseline

- Production major: PostgreSQL 16
- Pinned maintenance release after this hardening cycle: 16.15
- Current major remains supported through November 9, 2028.
- No PostgreSQL major-version change is part of the dashboard/dependency modernization PR.

## Candidate target

PostgreSQL 18.6 is the current stable release in the PostgreSQL 18 line as of August 23, 2026. PostgreSQL 19 is still beta and is not a production target.

A 16 → 18 production migration must be treated as a database migration project, not as an ordinary container-tag refresh.

## Preconditions

1. Inventory extensions, collations, custom types, roles, ownership, privileges, scheduled jobs, and database sizes.
2. Capture schema-only and full logical backups from the production-equivalent database.
3. Record database settings and extension versions.
4. Capture query-latency, connection-count, storage, and migration-duration baselines.
5. Verify current application migrations are at Alembic head.
6. Confirm PostgreSQL 18 compatible versions of every required extension.
7. Keep the existing PostgreSQL 16 volume untouched until the migration is accepted.

## Required backup and restore evidence

Before changing the production major:

- create a full `pg_dump`/`pg_dumpall --globals-only` backup;
- verify backup checksums;
- restore into a clean PostgreSQL 18 instance;
- run Alembic verification against the restored database;
- run backend tests and e2e smoke tests against the restored database;
- compare row counts for critical tenant, auth, billing, marketplace, scheduler, content, audit, and event tables;
- perform at least one timed rollback rehearsal back to PostgreSQL 16.

A backup that has not been successfully restored is not accepted as rollback evidence.

## Migration rehearsal

Use an isolated copy of production-equivalent data.

1. Freeze writes or capture a final consistent logical backup.
2. Restore globals and database content into PostgreSQL 18.6.
3. Apply/verify Alembic head.
4. Start zDash with all safety defaults locked:
   - `DRY_RUN=true`
   - `LIVE_TRADING_ACK=false`
   - `MT5_ENABLED=false`
   - `PRODUCTION_ALLOW_LIVE_ACTIONS=false`
   - `RISK_GUARDIAN_ENABLED=true`
5. Run auth/RBAC/tenant-isolation tests.
6. Run API envelope and WebSocket/realtime smoke tests.
7. Run backup-after-upgrade and restore-after-upgrade drills.
8. Compare query plans and latency for critical endpoints.

## Go criteria

All of the following are required:

- backup restore succeeds;
- extension compatibility is confirmed;
- Alembic reports head cleanly;
- backend and e2e suites pass;
- tenant isolation and authorization regressions pass;
- no critical query regression is observed;
- rollback to the untouched PostgreSQL 16 copy has been rehearsed successfully;
- an operator has an explicit maintenance and rollback window.

## Rollback criteria

Rollback immediately if any of the following occurs during cutover:

- migration or restore checksum mismatch;
- missing extension or incompatible collation;
- authorization/tenant-isolation regression;
- data-count mismatch in critical tables;
- repeated database process crash;
- unacceptable latency regression;
- Alembic cannot verify the expected head;
- application health or auth smoke tests fail.

Rollback means stopping writes to PostgreSQL 18 and returning application traffic to the preserved PostgreSQL 16 dataset. Do not attempt an in-place downgrade.

## Execution boundary

This document authorizes planning and rehearsal only. The production major will not be changed until restore and rollback evidence from an actual production-equivalent database is attached to a dedicated PostgreSQL migration PR.

## Evaluation log — 2026-08-23 (local rehearsal, empty databases)

Feasibility evidence gathered against PostgreSQL 18.6 (`postgres:18.6-alpine`) and
PostgreSQL 16.15 (`postgres:16.15-alpine`) containers using the refreshed rc3 locks.

| Check | Result |
| --- | --- |
| Alembic `upgrade -> head` (20260805_0001) on PostgreSQL 18.6 | PASS |
| Full backend suite (732 tests) against PostgreSQL 18.6 via psycopg | PASS (exit 0) |
| Migration-only schema parity, PG 16.15 vs PG 18.6 (19 tables each) | PASS (identical table sets) |
| `pg_dump` from PG 18.6 + restore into clean database | PASS |
| Alembic `current` on restored database | PASS (head) |
| Row-count spot check on critical tables post-restore | PASS |

No extensions are used by current migrations; driver is `psycopg` (3.x), which
connects to both majors without changes.

Outstanding before any production cutover (per Preconditions and Required
backup/restore evidence above): production-equivalent data restore, timed
rollback rehearsal back to PG 16, latency baseline comparison, and operator
maintenance window. These require production access and remain blocking.
