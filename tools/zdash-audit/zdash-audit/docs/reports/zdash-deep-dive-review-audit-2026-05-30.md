# zDash Deep Dive Review + Audit Report

Generated: `2026-05-30T13:03:42+00:00`  
Repository: `cvsz/zdash`  
Audit type: static architecture, safety, security, frontend/backend, CI, release-readiness, and deep-source-scan plan

---

## 1. Executive Summary

`cvsz/zdash` is positioned as a safety-first AI operations dashboard and agent runtime for staged automation, trading simulation, governance, observability, and enterprise control workflows.

Current assessment:

```text
Architecture direction:       Strong
Safety-by-default posture:    Strong
Frontend dashboard scope:     Broad and coherent
Backend/API scope:            Broad, needs enforced gates and proof
Security posture:             Good documentation baseline, needs automated evidence
Release readiness:            HOLD until local validation output is captured
Production readiness:         HOLD until fail-closed production config tests pass
```

Final decision:

```text
RELEASE DECISION: HOLD FOR VALIDATION
```

Reason:

```text
This audit reviewed public repo documentation and generated a full local deep-scan plan, but did not execute repo tests, builds, Docker validation, secret scans, or runtime smoke tests inside the actual repo checkout.
```

---

## 2. Source Facts Used

Observed public repo facts:

```text
Repository: cvsz/zdash
Purpose: safety-first AI operations dashboard and agent runtime
Backend: FastAPI on 0.0.0.0:8005
Frontend: React/Vite on 0.0.0.0:5173
Node: Node 20 LTS via nvm
Python: Python 3.11+ / 3.12 tested
Trading: simulation/dry-run only by default
IoT: dry-run + confirmation-gated by default
Social posting: dry-run + approval-gated by default
Strategy promotion: disabled by default
Cloudflare source of truth: cvsz/zeaz-platform
```

---

## 3. Repository Role and Ownership

### zDash owns

```text
application code
local config defaults
backend implementation
frontend implementation
tests
docs
phase prompts
dashboard UI
agent runtime
safety-first behavior
```

### zeaz-platform owns

```text
Cloudflare DNS
Pages/Tunnel routing
Access
WAF
API Shield
edge health checks
production support-domain rollout
```

Audit recommendation:

```text
Do not move Cloudflare mutation logic directly into zDash.
Use zDash as app source of truth and zeaz-platform as edge/infrastructure source of truth.
```

---

## 4. Runtime and Developer Workflow Review

Expected runtime:

```text
Backend:
  cd ~/zdash/backend
  source .venv/bin/activate
  uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload

Frontend:
  source ~/.nvm/nvm.sh
  nvm use 20
  cd ~/zdash/frontend
  npm run dev -- --host 0.0.0.0 --port 5173
```

Health checks:

```text
http://localhost:8005/health
http://localhost:8005/api
http://localhost:5173
```

Audit findings:

| Severity | Finding | Recommendation |
|---|---|---|
| P1 | Backend and frontend ports are fixed and documented | Preserve `8005` and `5173` in scripts/tests |
| P1 | Node uses nvm, not apt npm | Add installer guard preventing apt npm usage |
| P1 | Mock fallback is core UX behavior | Test degraded/offline UI explicitly |
| P2 | VM URL examples are environment-specific | Keep local and VM URLs clearly separate |

---

## 5. Safety Audit

Documented high-risk capabilities:

```text
trading
automation
IoT
social posting
update workflows
support bundles
fleet operations
marketplace/plugin concepts
security operations
```

Required safety defaults:

```text
live trading: disabled
real broker order execution: disabled
real IoT power actions: disabled
real social posting: disabled
secret export: disabled
real infrastructure mutation: disabled
real update apply/rollback: disabled
raw shell relay: disabled
unreviewed plugin execution: disabled
destructive automation: disabled
```

Required non-bypass gates:

```text
Guardian risk checks
drawdown guard
kill switch / halt flag
content approval
RBAC
tenant isolation
audit logging
policy/certification/attestation gates
backup/readiness checks before mutation
```

### Safety findings

#### P0-SAFETY-001 — Production fail-closed validator required

Risk:

```text
A production deployment could accidentally enable unsafe flags through environment variables.
```

Required tests:

```text
test_production_requires_auth_enabled
test_production_rejects_default_jwt_secret
test_production_rejects_live_trading_without_gate
test_production_rejects_iot_real_actions_without_confirmation_policy
test_production_rejects_social_auto_post_without_approval_policy
test_support_bundle_excludes_secrets_by_default
```

#### P0-SAFETY-002 — High-risk action policy must be centralized

All high-risk action paths should pass through one policy gate:

```text
auth -> RBAC -> tenant scope -> safety policy -> typed confirmation -> audit event -> adapter
```

High-risk classes:

```text
trading_order
iot_power
social_publish
infra_mutation
update_apply
rollback_execute
plugin_execute
support_bundle_export
secret_export
raw_shell
```

#### P1-SAFETY-003 — UI safety state must be impossible to miss

Required UI states:

```text
DRY_RUN ACTIVE
Guardian enabled
Kill switch / halt state
Risk approval required
Social dry-run
IoT dry-run
Provider safe mode
Simulated mode banner
```

---

## 6. Frontend Audit

Documented frontend architecture:

```text
layout components:
  frontend/src/components/layout/
  Sidebar
  Topbar
  PageHeader

pages:
  Dashboard
  Team Roster
  Trading
  Risk
  Scheduler
  Backtests
  Content
  IoT
  Org Map
  Logs
  Settings

API:
  frontend/src/api/client.ts
  frontend/src/api/endpoints.ts
  frontend/src/api/mockData.ts
```

Environment defaults:

```text
VITE_APP_NAME=zDash
VITE_API_BASE_URL=http://localhost:8005
VITE_ENABLE_MOCK_FALLBACK=true
VITE_POLL_INTERVAL_MS=5000
VITE_DEFAULT_THEME=dark
VITE_SHOW_SAFETY_BANNERS=true
```

### Frontend findings

| Severity | Finding | Action |
|---|---|---|
| P1 | Mock fallback can hide backend outages | Show clear simulated/degraded mode banner |
| P1 | High-risk UI needs disabled states | Add tests for disabled buttons and confirmations |
| P1 | `VITE_*` variables are browser-exposed | Add denylist test for secret-like frontend env vars |
| P2 | Many dashboard pages increase regression surface | Add smoke render test per route |
| P2 | Safety banners rely on env flag | Ensure production cannot hide safety banners on high-risk pages |

Required tests:

```text
dashboard_renders
all_routes_render
safety_banner_visible
dry_run_badge_visible
mock_fallback_banner_visible
high_risk_actions_disabled_by_default
typed_confirmation_required_for_real_mode
no_secret_like_vite_vars_rendered
```

---

## 7. Backend Audit

Expected backend architecture:

```text
FastAPI backend
Python 3.11+ / 3.12
ruff lint
pytest tests
httpx API tests
backend/app/
backend/tests/
backend/pyproject.toml
backend/requirements.txt
```

Required backend controls:

```text
consistent API envelope
input validation
auth/RBAC
tenant isolation
rate limiting for high-risk routes
audit logging
provider adapter fail-safe behavior
production config validation
safe error responses
health/readiness endpoints
```

### Backend findings

| Severity | Finding | Action |
|---|---|---|
| P0 | High-risk routes require enforceable policy | Add central policy dependency/middleware |
| P0 | Production config must fail closed | Add startup validator + tests |
| P1 | Provider adapters must fail safely | Add contract test matrix |
| P1 | Audit logs must be append-only for real actions | Add audit schema tests |
| P2 | Health should separate live/ready/dependency status | Add `/health/live`, `/health/ready`, `/health/dependencies` if absent |

Required backend tests:

```text
test_health_endpoint
test_api_envelope_shape
test_auth_required_for_admin_routes
test_rbac_denies_non_admin_high_risk_action
test_tenant_isolation
test_guardian_blocks_unsafe_action
test_kill_switch_blocks_action
test_provider_missing_credentials_fails_safe
test_provider_disabled_fails_safe
test_audit_event_written_for_high_risk_action
```

---

## 8. Agent and Phase Workflow Audit

Documented roster includes stable backend/API IDs and display names, with `docs/prompt/agent-roster.prompt` as the canonical reference.

Stable IDs to preserve:

```text
ceo
janie
guardian
editor
social
graphic
trading
joe
friday
```

Audit requirements:

```text
[ ] Stable IDs never renamed in backend/API contracts
[ ] Display names can change only in docs/UI metadata
[ ] Agent routes/events/tests use stable IDs
[ ] Phase prompts are traceable to implemented files and tests
```

Required phase matrix:

```text
docs/reports/phase-traceability-matrix.md
```

Columns:

```text
Phase
Prompt file
Feature area
Implemented files
Tests
Docs
Safety gates
Status
Last validated
```

---

## 9. CI/CD and Release Audit

Repository layout indicates `.github/workflows/` for CI, frontend CI, and security CI.

Required release gates:

```text
backend lint
backend tests
frontend tests
frontend build
secret scan
safety scan
docker compose config
artifact scan
phase traceability matrix
release checklist
rollback docs
```

Recommended branch protection:

```text
require PR
require CI
require security scan
require no unresolved P0/P1 findings
require signed release tag for final release
```

---

## 10. Docker and Deployment Audit

Expected files:

```text
docker-compose.yml
docker-compose.prod.yml
infra/docker/backend.Dockerfile
infra/docker/frontend.Dockerfile
```

Required checks:

```text
docker compose config
docker compose -f docker-compose.prod.yml config
docker build backend image
docker build frontend image
no secrets baked into image
healthchecks configured
non-root runtime where practical
minimal production image
```

---

## 11. Security Checklist

Immediate security checks:

```text
[ ] No `.env` committed
[ ] No private keys committed
[ ] No API keys committed
[ ] No Cloudflare tokens committed
[ ] No OpenAI keys committed
[ ] No GitHub tokens committed
[ ] No database URLs with credentials committed
[ ] `.env.example` uses placeholders only
[ ] logs do not include secrets
[ ] support bundles exclude secrets by default
[ ] deployment packs exclude secrets by default
```

Search patterns:

```text
OPENAI_API_KEY
CLOUDFLARE_API_TOKEN
GITHUB_TOKEN
JWT_SECRET
PRIVATE KEY
DATABASE_URL
PASSWORD
SECRET
TOKEN
API_KEY
```

Do not print detected secret values. Report only file path and variable/pattern name.

---

## 12. Deep Local Scan Script Output

Run included script:

```bash
scripts/deep-scan-zdash.sh
```

It creates:

```text
reports/00-summary.md
reports/01-file-inventory.txt
reports/02-source-inventory.txt
reports/03-functions-classes-components.txt
reports/04-routes-api.txt
reports/05-env-vars.txt
reports/06-package-make-scripts.txt
reports/07-security-patterns-redacted.txt
reports/08-docker-ci-inventory.txt
reports/09-validation-log.md
reports/10-remediation-plan.md
```

---

## 13. Priority Remediation Plan

### P0 — Block final release

```text
[ ] Run full validation and capture logs
[ ] Add production fail-closed validator tests
[ ] Add high-risk policy gate tests
[ ] Add secret scan over tracked files and artifacts
[ ] Add route smoke tests for all frontend pages
[ ] Add provider fail-safe contract tests
```

### P1 — Required before production prep

```text
[ ] Add phase traceability matrix
[ ] Add release readiness report
[ ] Add rollback runbook
[ ] Add Docker config validation in CI
[ ] Add frontend safety-state tests
[ ] Add backend audit-event tests
```

### P2 — Enterprise hardening

```text
[ ] Add SBOM generation
[ ] Add SLO definitions
[ ] Add incident response runbook
[ ] Add backup/restore proof
[ ] Add dependency update policy
[ ] Add signed release attestation
```

---

## 14. Final Recommendation

Current release decision:

```text
HOLD
```

Move to release candidate only after:

```text
make safety-scan
make validate-fast
make validate
docker compose config
frontend route smoke tests
provider contract tests
production fail-closed tests
```

Recommended next commit:

```text
docs: add zDash deep dive audit and final release gates
```
