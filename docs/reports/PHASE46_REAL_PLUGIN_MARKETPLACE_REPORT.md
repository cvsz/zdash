# Phase 46 — Real Plugin Marketplace

## Objective

Replace the mock plugin marketplace with a DB-backed, safety-gated production
plugin marketplace. All plugins stored in SQL tables, actions audited, built-ins
seeded on startup, frontend fully wired.

## Deliverables

### Backend

| File | Lines | Purpose |
|------|-------|---------|
| `app/marketplace/models.py` | 173 | ORM models: PluginManifest, PluginInstallation, PluginActionRun; Pydantic schema; serialisers |
| `app/marketplace/builtins.py` | 118 | 6 built-in PluginManifest definitions |
| `app/marketplace/plugin_registry.py` | 213 | DB-backed registry: seed_builtins, list/get/register/validate helpers |
| `app/marketplace/plugin_runtime.py` | 251 | Safe action runners: 6 builtin entrypoints, always dry_run, audit-logged |
| `app/marketplace/plugin_service.py` | 390 | Full lifecycle: validate_install, install, enable, disable, uninstall, run with audit/events/billing |
| `app/marketplace/safety.py` | 6 | Action gate: blocks live_trade, real_iot, real_social |
| `app/db/repositories.py` | 508 | New PluginManifestRepository + PluginActionRunRepository classes |
| `app/api/marketplace.py` | 289 | All endpoints return `{ok, data, error, timestamp}` envelope |

### Frontend

| File | Lines | Purpose |
|------|-------|---------|
| `frontend/src/pages/Marketplace.tsx` | 180 | Search/category/status filters, action loading spinners, error banner |
| `frontend/src/components/marketplace/PluginDetailPanel.tsx` | 312 | Config JSON editor, dry-run action console, output display |
| `frontend/src/components/marketplace/PluginCard.tsx` | 97 | Safety badge, category, install/view buttons |
| `frontend/src/components/marketplace/PluginGrid.tsx` | 91 | Filterable grid with search + category tabs |
| `frontend/src/components/marketplace/InstalledPluginTable.tsx` | 119 | Enable/disable/uninstall actions |
| `frontend/src/hooks/useMarketplace.ts` | 131 | search/category/status filter state, full lifecycle |
| `frontend/src/api/endpoints.ts` | 1293 | Search/category/status params on list; listPluginCategories; source_type/source_ref/checksum |
| `frontend/src/api/types.ts` | — | PluginManifest with source_type, source_ref, checksum |

### Tests (new)

| File | Tests | Purpose |
|------|-------|---------|
| `backend/app/tests/test_marketplace_real_registry.py` | 14 | DB-backed registry: seed, list, get, register, validate with SQLite |
| `backend/app/tests/test_marketplace_api_envelope.py` | 12 | All API endpoints return correct envelope format |
| `backend/app/tests/test_marketplace_action_runner.py` | 11 | Each builtin action runner produces correct output |
| `frontend/src/tests/MarketplaceActions.test.tsx` | 7 | Action UI: install, enable/disable, console, dry-run form |

### Docs

| File | Purpose |
|------|---------|
| `docs/runbooks/REAL_PLUGIN_MARKETPLACE.md` | Runbook with architecture, components, API table, safety, testing |
| `docs/reports/PHASE46_REAL_PLUGIN_MARKETPLACE_REPORT.md` | This report |

## Safety Compliance

- [x] All actions default to `dry_run=True`
- [x] Builtin entrypoints use `builtin://` URI scheme (no filesystem execution)
- [x] Secret redaction in audit/event payloads
- [x] RBAC on all endpoints (marketplace_read/install/manage/run_plugin)
- [x] Tenant isolation via organization_id
- [x] Safety gate blocks live_trade, real_iot, real_social
- [x] Unknown entrypoints return error, never execute arbitrary code
- [x] Rollback plan: revert migrations, clear plugin_* tables, remove code

## Validation

- 610 backend tests pass (includes 37 marketplace-specific tests: 14 registry, 12 API envelope, 11 action runner)
- 110 frontend tests pass (includes 7 marketplace action UI tests)
- Frontend build succeeds
- Zero stderr during test runs
- Zero React act() warnings

## Safety Model

### Built-in Plugin Actions (Dry-Run Default)
All builtin plugin actions use `dry_run=True` by default. The plugin runtime (`app/marketplace/plugin_runtime.py`) wraps every action in audit logging and event emission. No builtin action can execute live trades, real IoT mutations, or real social posts — these are blocked by the safety gate in `app/marketplace/safety.py`.

### Unknown Entrypoints
Unknown entrypoints (non-builtin URIs) return an error response and never execute arbitrary code. The plugin runtime validates entrypoint URIs against the registered builtin registry before any execution attempt.

### Real Third-Party Plugin Runtime
Real external/third-party plugin execution is **not enabled by default**. The current architecture supports only `builtin://` entrypoints. Future external plugin support will require:
1. **Signed manifests** — cryptographic verification of plugin origin and integrity
2. **Sandbox execution** — isolated process or container runtime with resource limits
3. **Permission review** — explicit user approval for each permission scope
4. **Audit logging** — full action traceability for external plugins

### Safety Compliance
- [x] All actions default to `dry_run=True`
- [x] Builtin entrypoints use `builtin://` URI scheme (no filesystem execution)
- [x] Secret redaction in audit/event payloads
- [x] RBAC on all endpoints (marketplace_read/install/manage/run_plugin)
- [x] Tenant isolation via organization_id
- [x] Safety gate blocks live_trade, real_iot, real_social
- [x] Unknown entrypoints return error, never execute arbitrary code
- [x] Rollback plan: revert migrations, clear plugin_* tables, remove code

## Rollback

1. `git revert <merge-commit>` for Phase 46
2. Drop tables: `DROP TABLE plugin_action_runs; DROP TABLE plugin_installations; DROP TABLE plugin_manifests;`
3. If needed: restore mock fallback in `frontend/src/api/endpoints.ts`
4. Delete runbook + report
