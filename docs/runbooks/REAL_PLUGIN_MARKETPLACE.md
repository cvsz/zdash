# Real Plugin Marketplace — Runbook

## Overview

Phase 46 replaces the mock plugin marketplace with a DB-backed, safety-gated
production plugin marketplace. Plugins are stored in `plugin_manifests`,
installations in `plugin_installations`, and action runs in `plugin_action_runs`.

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Frontend     │────▶│  API Router       │────▶│  Plugin Service  │
│  Marketplace  │     │  /api/marketplace  │     │                  │
└──────────────┘     └──────────────────┘     └──┬───────────────┘
                                                 │
                     ┌───────────────────────────┼───────────────────┐
                     │                           │                   │
               ┌─────▼──────┐           ┌────────▼───────┐  ┌───────▼────────┐
               │ Plugin      │           │ Plugin          │  │ Safety          │
               │ Registry    │           │ Runtime          │  │ Gate            │
               │ (DB-backed)  │           │ (builtin://)     │  │ (check_plugin)  │
               └─────────────┘           └────────────────┘  └────────────────┘
```

## Key Components

| Component | File | Purpose |
|-----------|------|---------|
| **PluginManifest** | `app/marketplace/models.py` | ORM model — name, slug, version, entrypoint, safety level |
| **PluginInstallation** | `app/marketplace/models.py` | Tenant-scoped install record |
| **PluginActionRun** | `app/marketplace/models.py` | Audit trail for every action execution |
| **seed_builtins()** | `app/marketplace/plugin_registry.py` | Seeds 6 built-in manifests on DB init |
| **list_plugins()** | `app/marketplace/plugin_registry.py` | DB query with search/category/status filters |
| **register_plugin_manifest()** | `app/marketplace/plugin_registry.py` | Upsert by slug |
| **run_action()** | `app/marketplace/plugin_runtime.py` | Safe action runner, always dry_run=True |
| **install/run/enable/disable** | `app/marketplace/plugin_service.py` | Full lifecycle with audit, events, billing |
| **API router** | `app/api/marketplace.py` | All endpoints return `{ok, data, error, timestamp}` |

## Built-in Plugins

| Plugin | Slug | Entrypoint |
|--------|------|------------|
| Risk Summary | `zdash-risk-summary` | `builtin://risk-summary` |
| Backtest Reporter | `zdash-backtest-reporter` | `builtin://backtest-reporter` |
| Content Calendar | `zdash-content-calendar` | `builtin://content-calendar` |
| Scheduler Health | `zdash-scheduler-health` | `builtin://scheduler-health` |
| Alert Router | `zdash-alert-router` | `builtin://alert-router` |
| Tenant Audit Export | `zdash-tenant-audit-export` | `builtin://tenant-audit-export` |

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/marketplace/categories` | List distinct categories |
| GET | `/api/marketplace/plugins` | List with `?search=&category=&status=` |
| GET | `/api/marketplace/plugins/{id}` | Get single manifest |
| GET | `/api/marketplace/installations` | List tenant installations |
| POST | `/api/marketplace/install` | Install plugin |
| POST | `/api/marketplace/installations/{id}/enable` | Enable installation |
| POST | `/api/marketplace/installations/{id}/disable` | Disable installation |
| DELETE | `/api/marketplace/installations/{id}` | Uninstall |
| POST | `/api/marketplace/installations/{id}/run` | Run action (always dry-run) |
| POST | `/api/marketplace/manifest` | Admin-only: register/update manifest |

## Safety

- All plugin actions return `dry_run=True` regardless of input.
- Entrypoint URI scheme `builtin://` prevents filesystem execution.
- `check_plugin_action()` blocks `live_trade`, `real_iot`, `real_social` actions.
- Audit/event payloads redact keys containing `secret`, `password`, `token`, `key`, `credential`.
- Tenant isolation enforced via `organization_id` on installations.
- RBAC requires `marketplace_read`, `marketplace_install`, `marketplace_manage`, `marketplace_run_plugin` permissions.

## Testing

```bash
# Run all marketplace tests
cd backend && python -m pytest app/tests/test_marketplace_*.py -q

# Run frontend marketplace tests
cd frontend && npx vitest run src/tests/Marketplace*.test.tsx
```

## Adding a New Built-in Plugin

1. Add entrypoint function in `app/marketplace/plugin_runtime.py` (always return dict, keep read-only/mock).
2. Add a `PluginManifest` entry in `app/marketplace/builtins.py`.
3. Wire entrypoint in `run_action()` dispatch table.
4. Run `seed_builtins()` to upsert to DB.
5. Write action runner test in `test_marketplace_action_runner.py`.
