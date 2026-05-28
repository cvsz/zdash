# Marketplace Model

The Phase 10 marketplace is a tenant-scoped plugin catalog and installation workflow. It is sandbox-first and designed to extend zDash without weakening risk, approval, or tenant boundaries.

## Core entities

### PluginManifest

Fields:

- `id`
- `name`
- `slug`
- `version`
- `description`
- `author`
- `category`
- `status`
- `required_features`
- `required_permissions`
- `config_schema`
- `default_config`
- `entrypoint`
- `safety_level`
- `metadata`
- `created_at`
- `updated_at`

Allowed statuses:

- `draft`
- `review`
- `approved`
- `rejected`
- `deprecated`
- `disabled`

### PluginInstallation

Fields:

- `id`
- `organization_id`
- `workspace_id`
- `plugin_id`
- `version`
- `status`
- `config`
- `enabled`
- `installed_by`
- `installed_at`
- `updated_at`

Allowed install statuses:

- `installed`
- `enabled`
- `disabled`
- `failed`
- `removed`

### PluginActionResult

Fields:

- `plugin_id`
- `action`
- `ok`
- `message`
- `output`
- `dry_run`
- `timestamp`

## Built-in plugins

Default built-in plugins are intentionally safe and read-only/dry-run oriented:

- `zdash-risk-summary`
- `zdash-backtest-reporter`
- `zdash-content-calendar`
- `zdash-scheduler-health`

## Safety model

Plugins must be sandboxed by default:

```env
MARKETPLACE_REVIEW_REQUIRED=true
PLUGIN_RUNTIME_MODE=sandbox
PLUGIN_ALLOW_EXTERNAL_NETWORK=false
PLUGIN_ALLOW_SECRET_ACCESS=false
```

The safety checker blocks:

- external network access unless explicitly reviewed and enabled
- secret access unless explicitly reviewed and enabled
- live trading actions
- real IoT actions
- real social posting
- cross-tenant access

## Entitlements and quota

Plugin installation requires:

- active marketplace entitlement
- available `marketplace_plugins_installed` quota
- tenant-scoped permission
- plugin review/approval when review is required

## API surface

```text
GET    /api/marketplace/plugins
GET    /api/marketplace/plugins/{plugin_id}
GET    /api/marketplace/installations
POST   /api/marketplace/install
POST   /api/marketplace/installations/{installation_id}/enable
POST   /api/marketplace/installations/{installation_id}/disable
DELETE /api/marketplace/installations/{installation_id}
POST   /api/marketplace/installations/{installation_id}/run
```

All routes require authentication and tenant context. Plugin run events must be audited.

## Error codes

- `PLUGIN_NOT_FOUND`
- `PLUGIN_NOT_APPROVED`
- `PLUGIN_SAFETY_BLOCKED`
- `FEATURE_NOT_ENTITLED`
- `QUOTA_EXCEEDED`
- `TENANT_ACCESS_DENIED`

## Frontend requirements

The Marketplace page must show:

- plugin grid
- categories
- plugin details
- install/enable/disable/uninstall controls
- installed plugins table
- safety level and safety notes
- dry-run plugin action panel
- entitlement and quota warnings

No plugin UI should present a dry-run action as a real external effect.
