# Enterprise Customer Runbook

Use this runbook for enterprise onboarding, white-label setup, export/import support, license handling, and customer health review.

## Enterprise onboarding path

1. Create organization.
2. Create workspace.
3. Invite team.
4. Verify Victor Hale / Guardian risk controls.
5. Run first dry-run scan.
6. Run first backtest.
7. Create first content item.
8. Review scheduler jobs.
9. Configure billing.
10. Review production safety check.

## License support

License operations:

```bash
curl http://localhost:8005/api/enterprise/license -H "Authorization: Bearer TOKEN"
curl -X POST http://localhost:8005/api/enterprise/license/apply \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"license_key": "LICENSE_VALUE"}'
```

Rules:

- Store only license hashes.
- License keys must never be logged.
- Invalid licenses must not disable safe/free mode.
- Licenses must not disable production safety lock.

## Branding support

Branding settings are tenant scoped:

- brand name
- logo URL
- primary color
- accent color
- support email
- custom domain placeholder

Rules:

- Validate color values.
- Escape custom text.
- Do not allow script injection.
- Custom domain/Cloudflare edge work belongs in `cvsz/zeaz-platform`.

## Export/import support

Export APIs:

```bash
curl http://localhost:8005/api/enterprise/exports -H "Authorization: Bearer TOKEN"
curl -X POST http://localhost:8005/api/enterprise/exports \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"export_type": "support", "include_secrets": false}'
```

Rules:

- Secrets are excluded by default.
- Secret export requires admin authority and typed confirmation: `CONFIRM_SECRET_EXPORT`.
- Exports are tenant scoped.
- Every export must create an audit event.

## Customer health review

Check:

```bash
curl http://localhost:8005/api/enterprise/customer-health -H "Authorization: Bearer TOKEN"
curl http://localhost:8005/api/enterprise/onboarding -H "Authorization: Bearer TOKEN"
```

Health should reflect onboarding progress and safe readiness, not commercial pressure or unsafe enablement.

## Cloudflare operator handoff

For `zdash.zeaz.dev`, custom domains, DNS, Tunnel, Access, WAF, rate limiting, TLS, and edge health checks, hand off to:

```text
cvsz/zeaz-platform
```

Do not store Cloudflare tokens or zone/account IDs in `cvsz/zdash`.

## Escalation triggers

Escalate immediately if:

- customer sees another tenant's data
- export includes secrets unexpectedly
- branding allows script injection
- license appears to disable safety locks
- custom domain routes bypass authentication or WAF expectations

## Post-support checklist

- Audit event exists.
- No secrets were exposed.
- Tenant isolation verified.
- Safety defaults unchanged.
- Docs/runbook updated if the support process changed.
