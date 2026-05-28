# Phase 10 · SaaS Monetization + Marketplace + Enterprise Packaging

Phase 10 adds the commercial packaging layer for zDash while preserving the safety-first operating model established in Phases 01–09.

## Scope

Phase 10 covers:

- billing plans and subscription lifecycle
- usage metering and quota enforcement
- feature entitlements
- mock billing and Stripe-compatible adapter shell
- plugin marketplace and sandbox runtime
- enterprise license model
- white-label branding
- export/import packaging
- customer onboarding and health tracking
- frontend pages for billing, usage, marketplace, enterprise, and onboarding

## Safety invariants

The commercial layer must not weaken runtime safety:

- `DRY_RUN=true` remains the safe default.
- `LIVE_TRADING_ACK=false` remains the safe default.
- `SOCIAL_DRY_RUN=true` and `SOCIAL_APPROVAL_REQUIRED=true` remain the safe defaults.
- `IOT_DRY_RUN=true` and `IOT_REQUIRE_CONFIRMATION=true` remain the safe defaults.
- `PRODUCTION_SAFETY_LOCK=true` remains the safe default.
- Enterprise licenses cannot disable production safety locks.
- Marketplace plugins cannot execute live trading, real IoT actions, or real social posting.
- Exports exclude secrets by default.

## Backend modules

Phase 10 backend surface:

```text
backend/app/billing/
backend/app/marketplace/
backend/app/enterprise/
backend/app/api/billing.py
backend/app/api/marketplace.py
backend/app/api/enterprise.py
```

## Frontend modules

Phase 10 frontend surface:

```text
/frontend/src/pages/Billing.tsx
/frontend/src/pages/Usage.tsx
/frontend/src/pages/Marketplace.tsx
/frontend/src/pages/Enterprise.tsx
/frontend/src/pages/Onboarding.tsx
/frontend/src/components/billing/
/frontend/src/components/marketplace/
/frontend/src/components/enterprise/
/frontend/src/hooks/useBilling.ts
/frontend/src/hooks/useUsage.ts
/frontend/src/hooks/useMarketplace.ts
/frontend/src/hooks/useEnterprise.ts
```

## API examples

All examples use backend port `8005`.

```bash
curl http://localhost:8005/api/billing/plans -H "Authorization: Bearer TOKEN"
curl http://localhost:8005/api/billing/status -H "Authorization: Bearer TOKEN"
curl http://localhost:8005/api/billing/usage -H "Authorization: Bearer TOKEN"
curl -X POST http://localhost:8005/api/billing/mock/apply-plan \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_tier": "pro"}'
curl http://localhost:8005/api/marketplace/plugins -H "Authorization: Bearer TOKEN"
curl http://localhost:8005/api/enterprise/status -H "Authorization: Bearer TOKEN"
```

## Production posture

- Billing defaults to the mock provider in development.
- Stripe is disabled unless explicitly configured.
- The Stripe adapter is a replaceable shell and must never log secrets.
- No raw card data is stored or processed by zDash.
- Cloudflare DNS, Tunnel, Access, WAF, and edge operations remain in `cvsz/zeaz-platform`.

## Validation

```bash
cd backend
source .venv/bin/activate
python -m ruff check app tests
python -B -m pytest -q

cd ../frontend
source ~/.nvm/nvm.sh
nvm use 20
npm test
npm run build

cd ..
docker build -f infra/docker/backend.Dockerfile .
docker build -f infra/docker/frontend.Dockerfile .
docker build -f infra/docker/nginx.Dockerfile .
docker compose config
docker compose -f docker-compose.prod.yml config
bash .codex/cloud/maintenance.sh
```

## Phase 11 handoff

Phase 11 can build AI Ops, governance, compliance, and marketplace expansion on top of the Phase 10 commercial model. Preserve tenant isolation, entitlement checks, plugin sandboxing, audit logs, and dry-run defaults.
