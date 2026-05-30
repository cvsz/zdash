# Production Fail-Closed Policy

## Principle

In production, every unsafe configuration must cause the application to fail closed (refuse to start or block execution) rather than fail open (proceed with reduced safety).

## Unsafe flags

The following flags are considered unsafe in production:

| Flag | Unsafe value | Rationale |
|------|-------------|-----------|
| `DRY_RUN` | `false` | Live execution without explicit guard |
| `AUTH_ENABLED` | `false` | No authentication on endpoints |
| `PRODUCTION_SAFETY_LOCK` | `false` | Disables production safety checks |
| `LIVE_TRADING_ACK` | `true` with default JWT secret | Unsafe live trading |
| `SOCIAL_DRY_RUN` | `false` without approval gates | Real posting without approval |
| `IOT_DRY_RUN` | `false` without confirmation gates | Real device actions without confirmation |
| `SUPPORT_BUNDLE_INCLUDE_SECRETS` | `true` | Secret export |
| `DEPLOYMENT_PACK_INCLUDE_SECRETS` | `true` | Secret export |

## Blocked production defaults

The following configurations are blocked when `APP_ENV=production`:

1. **Default JWT secret** — `JWT_SECRET_KEY` must be non-default.
2. **Default admin password** — `DEFAULT_ADMIN_PASSWORD` must be non-default.
3. **Wildcard CORS with credentials** — `CORS_ALLOW_ORIGINS=*` + `CORS_ALLOW_CREDENTIALS=true` blocked.
4. **DRY_RUN=false with PRODUCTION_SAFETY_LOCK=true** — blocked.
5. **Live trading with default secret** — blocked.
6. **Real social posting without approval** — requires `SOCIAL_APPROVAL_REQUIRED=true` and `SOCIAL_REAL_POSTING_APPROVED=true`.
7. **Real IoT actions without confirmation** — requires `IOT_REQUIRE_CONFIRMATION=true` and `IOT_REAL_ACTIONS_APPROVED=true`.

## Required confirmations

| Action | Confirmation required |
|--------|----------------------|
| DRY_RUN=false | Explicit env + PRODUCTION_SAFETY_LOCK=false + PRODUCTION_ALLOW_LIVE_ACTIONS=true |
| Live trading | LIVE_TRADING_ACK=true + JWT_SECRET_KEY non-default + all Guardian gates |
| Social auto-post | SOCIAL_APPROVAL_REQUIRED=true + SOCIAL_REAL_POSTING_APPROVED=true |
| IoT real actions | IOT_REQUIRE_CONFIRMATION=true + IOT_REAL_ACTIONS_APPROVED=true |

## Secret policy

- Never commit secrets to source.
- Never bake secrets into Docker images.
- Never export secrets by default in support bundles or deployment packs.
- Use `.env.example` with placeholders only.
- Use `scripts/production/generate-prod-env.sh` to generate random secrets.
- Rotate secrets before production deployment.

## Audit policy

Every high-risk action must produce an audit event with:
- Actor (user ID + email)
- Action type
- Resource type + ID
- Timestamp
- Result (success/failure)

## Operator approval policy

Operator approval is required for:
- Live trading enable
- Real social posting
- Real IoT device actions
- Infrastructure mutations
- Plugin execution
- Support bundle export with secrets
- Any action that sets DRY_RUN=false

## Enforcement

The production safety check (`GET /api/admin/safety-check`) validates all policies at runtime. If any check fails, the endpoint returns `status: "blocked"` with a list of blockers.
