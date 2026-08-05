# Marketing Intelligence Dashboard

The Marketing Intelligence dashboard adapts the operational patterns from the referenced Content Dashboard demo into the existing zDash content stack.

## Route

- Frontend: `/marketing`
- API: `GET /api/marketing/overview`
- Authentication: required

## What is live

The dashboard reads these values from the local zDash content pipeline:

- total content assets;
- items awaiting approval or a terminal decision;
- scheduled items;
- published items;
- scheduled content details when available.

These values carry `source: live` in the API response.

## What is sample

The first vertical slice does not claim access to external marketing platforms. Until dedicated provider connectors are configured, the following modules contain clearly labelled sample records:

- hook performance;
- competitor intelligence;
- trend signals;
- advertising and budget recommendations;
- calendar examples when no local item is scheduled.

Every such record carries `source: sample`. The UI displays a source badge and a provenance disclaimer. Sample recommendations never mutate campaign budgets or publish content.

## Operational flow

```text
Sources and connectors
        -> Marketing intelligence
        -> Content production
        -> Human approval
        -> Scheduling and distribution
        -> Performance learning
```

The system-map cards link to existing zDash routes where an operational module already exists:

- `/settings` for connectors and configuration;
- `/content` for content creation, review, and approval;
- `/scheduler` for scheduled operations.

## Local validation

```bash
cd backend
pytest tests/test_marketing_dashboard.py

cd ../frontend
npm ci
npm run typecheck
npm run test -- --run
npm run build
```

## Provider integration boundary

Future live connectors should implement read-only ingestion adapters first. Normalize provider payloads into the dashboard contracts, preserve source timestamps, and retain provider identifiers for auditability. Publishing, campaign mutation, and budget changes must remain approval-gated and idempotent.
