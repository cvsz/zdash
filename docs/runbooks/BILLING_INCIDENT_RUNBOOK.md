# Billing Incident Runbook

Use this runbook when billing, subscription, invoice, entitlement, quota, or provider adapter behavior is degraded.

## Severity guide

- SEV1: Paid customers are incorrectly blocked or all billing APIs fail closed in production.
- SEV2: Checkout, billing portal, or invoice sync is unavailable.
- SEV3: Usage summary or quota display is stale but core features remain safe.

## First checks

```bash
curl http://localhost:8005/health
curl http://localhost:8005/api/billing/status -H "Authorization: Bearer TOKEN"
curl http://localhost:8005/api/billing/plans -H "Authorization: Bearer TOKEN"
curl http://localhost:8005/api/billing/usage -H "Authorization: Bearer TOKEN"
```

## Safety checks

Confirm these remain safe:

```env
BILLING_PROVIDER=mock
BILLING_FAIL_CLOSED=true
STRIPE_ENABLED=false
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

In production, real Stripe mode must have explicit config and must never log secrets.

## Triage

1. Check API health and logs.
2. Check tenant context headers.
3. Confirm subscription state for the organization.
4. Confirm plan catalog availability.
5. Confirm entitlement decision reason.
6. Confirm usage/quota summary.
7. Confirm audit log entries for billing actions.

## Common failures

### Provider not configured

Expected error:

```text
BILLING_PROVIDER_NOT_CONFIGURED
```

Action:

- Keep billing fail-closed if production.
- Use mock provider only in development or approved admin testing.

### Quota exceeded

Expected error:

```text
QUOTA_EXCEEDED
```

Action:

- Confirm usage summary.
- Confirm plan limits.
- Confirm tenant scope.
- Do not manually bypass quota in production.

### Subscription inactive

Expected error:

```text
SUBSCRIPTION_INACTIVE
```

Action:

- Confirm subscription status.
- Confirm current period dates.
- Confirm grace period.
- Apply only approved support action.

## Recovery

Development/mock recovery:

```bash
curl -X POST http://localhost:8005/api/billing/mock/apply-plan \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_tier": "pro"}'
```

Production recovery must use provider portal/API and audited admin actions. Do not edit database records manually unless there is an approved incident procedure and backup.

## Post-incident

- Export audit trail.
- Record root cause.
- Add regression test.
- Update entitlement/quota docs if behavior changed.
- Verify no payment secrets or raw card data were exposed.
