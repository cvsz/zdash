# Billing Model

The Phase 10 billing model is tenant-scoped and provider-adapter based. It supports local mock billing by default and Stripe-compatible integration only when explicitly configured.

## Plans

Plan tiers:

- `free`
- `starter`
- `pro`
- `enterprise`

Default plan catalog:

| Tier | Monthly | Workspaces | Users | Backtests/mo | Optimizations/mo | Content/mo | Scheduler jobs | Plugins | Support |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| free | 0 | 1 | 1 | 25 | 5 | 25 | 3 | 0 | community |
| starter | 29 | 2 | 3 | 250 | 25 | 250 | 10 | 3 | email |
| pro | 99 | 10 | 15 | 2500 | 250 | 2500 | 100 | 25 | priority |
| enterprise | custom | unlimited | unlimited | custom | custom | custom | custom | custom | dedicated |

## Core entities

- `BillingPlan`
- `Subscription`
- `UsageRecord`
- `UsageSummary`
- `Invoice`
- `EntitlementDecision`

Provider references such as customer IDs, subscription IDs, and invoice IDs may be stored. Raw card data must never be stored.

## Entitlements

Entitlement checks gate paid or limited features:

- trading scanner
- risk guardian
- scheduler
- backtesting
- optimization
- content pipeline
- IoT
- marketplace
- white label
- audit export
- enterprise export
- realtime stream

If billing is disabled in development, feature checks may allow access but must report mock/dev mode. If provider state is unavailable and `BILLING_FAIL_CLOSED=true`, paid features must fail closed.

## Usage metering

Tracked metrics include:

- `api_requests`
- `backtests_run`
- `optimizations_run`
- `content_items_created`
- `content_posts_attempted`
- `scheduler_jobs_created`
- `scheduler_jobs_run`
- `iot_actions_requested`
- `marketplace_plugins_installed`
- `worker_tasks_enqueued`
- `realtime_connections`
- `storage_mb_estimated`

Usage records are organization/workspace scoped. Secret payloads must never be recorded.

## Quotas

Quota checks run before expensive or externally impactful operations. If a quota is exceeded, APIs should use the standard error code:

```text
QUOTA_EXCEEDED
```

Warnings should surface above 80 percent usage. Quota enforcement must be tenant scoped.

## Provider adapters

`BillingProviderAdapter` defines:

- `create_customer(organization)`
- `create_checkout_session(organization_id, plan_id)`
- `get_subscription(provider_subscription_id)`
- `cancel_subscription(provider_subscription_id)`
- `create_billing_portal_session(organization_id)`
- `handle_webhook(payload, signature)`

## Mock provider

The mock provider is deterministic, local, and offline:

- fake customer IDs
- fake subscription IDs
- fake checkout URL
- fake billing portal URL
- no network calls

## Stripe shell

The Stripe adapter is intentionally safe:

- no crash if the SDK is missing
- disabled by default
- requires explicit config
- never logs secret keys
- webhook verification fails safely if the webhook secret is missing

## Required defaults

```env
BILLING_ENABLED=true
BILLING_PROVIDER=mock
BILLING_FAIL_CLOSED=true
STRIPE_ENABLED=false
USAGE_METERING_ENABLED=true
USAGE_ENFORCEMENT_ENABLED=true
```
