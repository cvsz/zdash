# Subscription Support Runbook

Use this runbook for customer support requests involving plan changes, subscription status, billing portal access, invoices, grace periods, and quota questions.

## Required context

Collect only non-sensitive context:

- organization ID or slug
- workspace ID when relevant
- user email or user ID
- current plan tier
- current subscription status
- request type
- timestamp

Never ask for or store raw card data, provider secret keys, or full payment credentials.

## Support flows

### View current billing state

```bash
curl http://localhost:8005/api/billing/status -H "Authorization: Bearer TOKEN"
curl http://localhost:8005/api/billing/subscription -H "Authorization: Bearer TOKEN"
curl http://localhost:8005/api/billing/invoices -H "Authorization: Bearer TOKEN"
```

### Start checkout

```bash
curl -X POST http://localhost:8005/api/billing/checkout \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "pro"}'
```

### Open billing portal

```bash
curl -X POST http://localhost:8005/api/billing/portal -H "Authorization: Bearer TOKEN"
```

### Development-only mock plan apply

```bash
curl -X POST http://localhost:8005/api/billing/mock/apply-plan \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_tier": "starter"}'
```

Mock plan apply is for development or approved admin support simulation only.

## Permissions

- `billing.read` can view billing state.
- `billing.manage` can start checkout, portal, cancellation, or subscription management flows.
- `billing.apply_mock_plan` is restricted to admin/development mode.

## Customer messaging

Keep messaging factual:

- Explain current plan and limits.
- Explain quota status and reset time.
- Do not promise trading outcomes or automation results.
- Do not claim billing changes enable live trading or bypass safety locks.

## Escalation

Escalate to engineering if:

- subscription is active but paid entitlement is blocked
- quota calculation differs from usage records
- invoice state does not match provider state
- webhook processing fails repeatedly
- customer sees cross-tenant data

Cross-tenant exposure is a security incident.

## Post-support checklist

- Confirm audit log entry exists.
- Confirm no secret data was collected.
- Confirm tenant isolation remained intact.
- Add regression coverage for confirmed defects.
