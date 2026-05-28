# Enterprise Packaging

Phase 10 enterprise packaging adds licensing, white-label branding, export/import packaging, onboarding, and customer-success readiness for tenant-scoped enterprise deployments.

## Enterprise license

`EnterpriseLicense` stores only a hash of the provided license key.

Core fields:

- `id`
- `organization_id`
- `license_key_hash`
- `status`
- `tier`
- `seats`
- `features`
- `expires_at`
- `offline_mode`
- `issued_to`
- `metadata`
- `created_at`
- `updated_at`

Rules:

- Store only license hashes.
- Invalid licenses must not disable free/core safe mode.
- Offline license mode may be supported.
- Licenses must never disable `PRODUCTION_SAFETY_LOCK`.

## White-label branding

`BrandingSettings` is organization/workspace scoped.

Fields:

- `brand_name`
- `logo_url`
- `primary_color`
- `accent_color`
- `support_email`
- `custom_domain`
- `metadata`

Rules:

- Validate color values.
- Escape and sanitize custom fields.
- Never allow script injection.
- Do not expose secrets through branding metadata.

## Export/import packaging

`ExportBundle` represents a safe export package.

Rules:

- Secrets are excluded by default.
- Secret export requires admin permission and typed confirmation: `CONFIRM_SECRET_EXPORT`.
- Export bundles are tenant scoped.
- Every export event must be audited.
- Import must validate tenant ownership and schema version.

## Onboarding checklist

Default steps:

- create organization
- create workspace
- invite team
- verify risk guardian
- run first dry-run scan
- run first backtest
- create first content item
- review scheduler jobs
- configure billing
- review production safety check

## Customer health

Customer health summarizes setup progress and safe readiness. It should combine onboarding progress, safety checks, billing status, workspace readiness, and recent operational events without exposing secrets.

## API surface

```text
GET  /api/enterprise/status
GET  /api/enterprise/license
POST /api/enterprise/license/apply
POST /api/enterprise/license/revoke
GET  /api/enterprise/branding
PATCH /api/enterprise/branding
POST /api/enterprise/branding/reset
GET  /api/enterprise/exports
POST /api/enterprise/exports
GET  /api/enterprise/exports/{bundle_id}
GET  /api/enterprise/onboarding
POST /api/enterprise/onboarding/complete-step
POST /api/enterprise/onboarding/reset
GET  /api/enterprise/customer-health
```

All routes require authentication and tenant context. License apply/revoke requires owner/admin authority. Branding requires owner/admin/operator authority. Export requires enterprise entitlement.

## Frontend pages

- `/enterprise` shows license, branding, export/import, onboarding, customer health, and white-label preview.
- `/onboarding` shows a step-by-step checklist, safety checklist, and dry-run quick actions.

## Cloudflare handoff

Custom domains and edge routing belong in `cvsz/zeaz-platform`. zDash stores safe placeholder settings and origin readiness only.
