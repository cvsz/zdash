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

- 490+ backend tests pass
- 96+ frontend tests pass
- Frontend build succeeds (2332 module build)
- Zero stderr during test runs
- Zero React act() warnings

## Rollback

1. `git revert <merge-commit>` for Phase 46
2. Drop tables: `DROP TABLE plugin_action_runs; DROP TABLE plugin_installations; DROP TABLE plugin_manifests;`
3. If needed: restore mock fallback in `frontend/src/api/endpoints.ts`
4. Delete runbook + report
