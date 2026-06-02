# Changelog

## v0.42.0-rc2 (2026-06-02) — P0-P2 Hardening Release

### Added
- Phase 43: Frontend API mock harness for test stability, mock service worker integration
- Phase 44: act-warning cleanup, async test stabilization, frontend lint remediation
- Phase 45: Zero-stderr frontend validation, error boundary hardening
- Phase 46: Real DB-backed plugin marketplace with builtin actions, dry-run gated
- Phase 47: Real DB-backed team workspace with RBAC, invitations, agent assignments
- Phase 48: P0–P2 production hardening pack — optimize fix, docs sync, SBOM generation, SLO definitions, incident response runbook, backup/restore runbook, dependency update policy, release attestation, release verifier

### P0 Hardening
- Performance optimize fix applied across backend and frontend
- Frontend normalization for consistent test behavior
- Zero-stderr validation stability achieved across all test runs
- All React act() warnings eliminated

### P1 Documentation Sync
- README Feature Map updated through Phase 48
- README Runtime Summary updated with marketplace, team workspace, plugin, strategy promotion status
- CHANGELOG updated with P0-P2 entries
- Phase 46 and Phase 47 reports updated with accurate test counts and safety language
- Phase 48 release notes and report created
- SBOM generation integrated into CI pipeline
- docs/ops/ directory with SLO definitions, dependency update policy
- docs/runbooks/INCIDENT_RESPONSE.md created with full severity framework
- docs/reports/generated/ directory created for auto-generated reports

### P2 Production Ops
- SBOM (Software Bill of Materials) generation in CI
- SLO definitions documented (availability, latency, error-rate, realtime, CI, backup, incident response)
- Incident response framework with SEV1–SEV4 severity levels and triage flow
- Backup/restore runbook with RTO < 1 hour, RPO < 24 hours
- Dependency update policy with weekly cadence, security patch SLA
- Release attestation for verifiable builds
- Release verifier for post-release validation

### Safety
- All trading remains simulation/dry-run only by default
- DRY_RUN=true, LIVE_TRADING_ACK=false, MT5_ENABLED=false
- PRODUCTION_ALLOW_LIVE_ACTIONS=false, RISK_GUARDIAN_ENABLED=true
- validate_production_config() fail-closed at startup
- High-risk action policy gate on sensitive endpoints
- No real social posting, IoT mutation, or broker execution enabled by default
- No secrets committed to repository
- Plugin execution remains dry-run/sandbox-gated by default
- Unknown plugin entrypoints return error, never execute arbitrary code
- Builtin plugin actions use `builtin://` URI scheme (no filesystem execution)

### Validation
- Backend: 610 pytest tests passing
- Frontend: 110 vitest tests passing (47 test files)
- Frontend build: production bundle
- Safety scan: PASSED
- Zero stderr during test runs
- Zero React act() warnings
- SBOM generation: verified

### Operations
- 35+ runbook documents covering all operations
- docs/ops/ directory added for operational policies
- docs/reports/generated/ directory for auto-generated reports
- SBOM generated in CI pipeline
- Incident response framework documented

### Known Limitations
- Backend uses SQLite by default for local development; production requires PostgreSQL
- SLO monitoring not yet automated (manual verification only)
- Some blueprint phases may be prompt-only until implemented
- passlib may emit Python crypt deprecation warning on Python 3.12

## v0.42.0-rc1 (2026-05-31) — Final Public Release Candidate

### Added
- Phase 36: Server command center with 9 management scripts (start, stop, status, health, logs, backup, db migration, reset) and 5 git safety scripts
- Phase 37: Realtime gateway stabilization with WebSocket channel validation, frontend RealtimeClient, useCollaboration WebSocket URL construction, and ContentPipeline approval-gated display
- Phase 38: Release readiness pack — release readiness report, rollback runbook, phase traceability matrix, go-live checklist
- Phase 39: Production dry-run verification — 4 verification scripts (runtime, health, rollback readiness, observability)
- Phase 40: Go-live rehearsal workflow — safety locks verification, evidence capture, full rehearsal orchestration
- Phase 41: Release automation — release readiness verification, evidence collection, release candidate creation, operator handoff manual
- Phase 42: Final public release pack — README update, CHANGELOG, VERSION freeze, quick start, installation, operations index, final release notes, final validation script

### Changed
- README.md updated with quick start, feature map, architecture summary, server commands, release/operator links
- Release decision moved from HOLD to GO across all documentation

### Fixed
- All mypy errors resolved (zero errors across 435 source files)
- React Router v7 future flags added to BrowserRouter in tests
- act() replaced with waitFor in RealtimeHooks tests
- move() replaced with toBe() in test assertions
- CI compose validation and lint fixes

### Safety
- All trading remains simulation/dry-run only by default
- DRY_RUN=true, LIVE_TRADING_ACK=false, MT5_ENABLED=false
- PRODUCTION_ALLOW_LIVE_ACTIONS=false, RISK_GUARDIAN_ENABLED=true
- validate_production_config() fail-closed at startup
- High-risk action policy gate on sensitive endpoints
- No real social posting, IoT mutation, or broker execution enabled by default
- No secrets committed to repository

### Operations
- 23 runbook documents covering all operations
- 9 server management scripts
- 7 production verification scripts
- 3 release automation scripts
- Full go-live rehearsal and evidence capture workflow
- Operator handoff manual with start/stop/health/logs/backup/rollback/safety/emergency procedures

### Validation
- Backend: 490 pytest tests passing
- Frontend: 90 vitest tests passing (44 test files)
- Frontend build: 2332 modules, production bundle
- Safety scan: PASSED
- mypy: zero errors across 435 source files
- Docker compose config: valid (dev + prod)

### Known Limitations
- Backend uses SQLite by default for local development; production requires PostgreSQL
- No SBOM generation in CI (future enhancement)
- No automated SLO monitoring (future enhancement)
- Some blueprint phases may be prompt-only until implemented
- passlib may emit Python crypt deprecation warning on Python 3.12
