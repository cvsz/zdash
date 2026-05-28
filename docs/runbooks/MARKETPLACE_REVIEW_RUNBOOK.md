# Marketplace Review Runbook

Use this runbook when reviewing, approving, disabling, or investigating marketplace plugins.

## Review principles

Marketplace plugins must preserve zDash safety boundaries:

- no live trading actions
- no real IoT actions
- no real social posting
- no external network by default
- no secret access by default
- tenant scoped execution
- audited install/run lifecycle

## Plugin intake checklist

For each plugin manifest, review:

- name, slug, and version
- author and category
- required features
- required permissions
- config schema and default config
- entrypoint
- safety level
- metadata
- status

Reject plugins that request broad or unclear permissions.

## Safety checks

Block or reject if the plugin attempts to:

- read environment secrets
- exfiltrate data
- call external networks without review
- execute shell commands
- route orders to brokers
- control real IoT devices
- publish social content for real
- bypass content approval
- bypass Victor Hale / Guardian risk checks
- access another tenant's data

## API checks

```bash
curl http://localhost:8005/api/marketplace/plugins -H "Authorization: Bearer TOKEN"
curl http://localhost:8005/api/marketplace/installations -H "Authorization: Bearer TOKEN"
```

## Installation support

When a user cannot install a plugin:

1. Confirm plugin exists.
2. Confirm plugin status is approved.
3. Confirm marketplace entitlement.
4. Confirm plugin quota.
5. Confirm workspace membership and permissions.
6. Confirm tenant context headers.

Expected errors:

- `PLUGIN_NOT_FOUND`
- `PLUGIN_NOT_APPROVED`
- `PLUGIN_SAFETY_BLOCKED`
- `FEATURE_NOT_ENTITLED`
- `QUOTA_EXCEEDED`
- `TENANT_ACCESS_DENIED`

## Incident response

If a plugin appears unsafe:

1. Disable the plugin manifest or affected installation.
2. Preserve audit logs and plugin action outputs.
3. Confirm no secrets were exposed.
4. Confirm no real-world action occurred.
5. Add a regression test to the safety checker.
6. Update plugin review guidance.

## Built-in plugin expectations

Built-in plugins should remain read-only or dry-run:

- `zdash-risk-summary`
- `zdash-backtest-reporter`
- `zdash-content-calendar`
- `zdash-scheduler-health`

## Post-review documentation

Record:

- reviewer
- decision
- reasons
- required changes
- allowed permissions
- safety level
- tenant impact
