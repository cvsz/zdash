# zDash v0.42.0-rc1 — Final Public Release Notes

**Version:** 0.42.0-rc1
**Date:** 2026-05-31
**Status:** RELEASE CANDIDATE
**Safety:** LOCKED

## Added

- **Phase 36**: Server command center — 9 server management scripts (start, stop, status, health, logs, backup, db migration, reset) and 5 git safety scripts (safe-push, squash, amend-signed, branch-from, gh-release)
- **Phase 37**: Realtime gateway stabilization — WebSocket channel validation, frontend RealtimeClient with 4 channel mappings, useCollaboration WebSocket URL construction, ContentPipeline approval-gated display, test isolation configuration
- **Phase 38**: Release readiness pack — release readiness report (GO), rollback runbook, phase traceability matrix (phases 01-37), go-live checklist
- **Phase 39**: Production dry-run verification — 4 verification scripts covering runtime, health, rollback readiness, and observability
- **Phase 40**: Go-live rehearsal workflow — safety locks verification, evidence capture, full 6-phase rehearsal orchestration
- **Phase 41**: Release automation — release readiness verification (25 checks), evidence collection, release candidate creation, operator handoff manual
- **Phase 42**: Final public release pack — README update with quick start and operator links, CHANGELOG, VERSION freeze (0.42.0-rc1), quick start guide, installation guide, operations index, final validation script
- **Phase 43**: Frontend API mock harness for test stability, mock service worker integration
- **Phase 44**: act-warning cleanup, async test stabilization, frontend lint remediation
- **Phase 45**: Zero-stderr frontend validation, error boundary hardening
- **Phase 46**: Real DB-backed plugin marketplace with builtin actions, dry-run gated
- **Phase 47**: Real DB-backed team workspace with RBAC, invitations, agent assignments
- **Phase 48**: P0–P2 production hardening pack — optimize fix, docs sync, SBOM, SLO definitions, incident response, backup/restore, dependency policy, release attestation, verifier

## Changed

- README.md updated with quick start, feature map, architecture summary, server commands, validation commands, release docs links, operator handoff links
- README Feature Map extended through Phase 48
- README Runtime Summary includes marketplace, team workspace, plugin, strategy promotion status
- Release decision moved from HOLD to GO across all documentation

## Fixed

- All mypy errors resolved (zero errors across 435 source files)
- React Router v7 future flags added to BrowserRouter in tests
- act() replaced with waitFor in RealtimeHooks tests
- CI compose validation and lint fixes
- Performance optimize fix applied
- Frontend normalization for consistent test behavior
- Zero-stderr validation stability achieved
- All React act() warnings eliminated

## Safety

- All trading remains simulation/dry-run only by default
- DRY_RUN=true, LIVE_TRADING_ACK=false, MT5_ENABLED=false
- PRODUCTION_ALLOW_LIVE_ACTIONS=false, RISK_GUARDIAN_ENABLED=true
- validate_production_config() fail-closed at startup
- High-risk action policy gate on sensitive endpoints
- No real social posting, IoT mutation, or broker execution enabled
- No secrets committed to repository
- Plugin execution remains dry-run/sandbox-gated by default
- Unknown plugin entrypoints return error, never execute arbitrary code

## Operations

- 35+ runbook documents covering all operations
- 9 server management scripts
- 7 production verification scripts
- 3 release automation scripts
- Full go-live rehearsal and evidence capture workflow
- Operator handoff manual with complete procedures
- docs/ops/ directory with SLO definitions and dependency update policy
- Incident response framework with SEV1–SEV4 severity levels
- SBOM generation in CI pipeline

## Validation

| Check | Result |
|-------|--------|
| Backend tests (pytest) | 610 PASSED |
| Frontend tests (vitest) | 110 PASSED (47 files) |
| Frontend build | PASSED |
| Safety scan | PASSED |
| mypy | Zero errors (435 source files) |
| Docker compose config | Valid (dev + prod) |
| Secret scan | No secrets tracked |
| Zero stderr during test runs | CONFIRMED |
| Zero React act() warnings | CONFIRMED |
| SBOM generation | VERIFIED |

## Known Limitations

- Backend uses SQLite by default for local development; production requires PostgreSQL
- SLO monitoring not yet automated (manual verification only)
- Backup/restore automation scripts documented but not integrated into Makefile
- Some blueprint phases may be prompt-only until implemented
- passlib may emit Python crypt deprecation warning on Python 3.12
- This release is not financial advice

## Links

- Repository: https://github.com/cvsz/zdash
- Support domain: https://zdash.zeaz.dev
- Operator handoff: docs/runbooks/OPERATOR_HANDOFF.md
- Rollback runbook: docs/runbooks/ROLLBACK_RUNBOOK.md
- Go-live checklist: docs/runbooks/GO_LIVE_CHECKLIST.md
