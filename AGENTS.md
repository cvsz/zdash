# zDash · Root Agent Guide

Repository: `cvsz/zdash`

Project: **⬡ zDash · FULL SYSTEM BLUEPRINT v2.0**

This file is the canonical repo-level guidance for Codex, Codex Cloud, ECC agents, and any coding agent working in this repository. Keep Codex Cloud custom instructions compact and point agents here for full details.

---

## 1. Mission

Implement zDash phase-by-phase with production-grade quality while preserving safety defaults.

The repository contains a staged implementation plan under `docs/prompt/` from `phase01.prompt` through `phase32.prompt`. Each phase extends the previous phases. Agents must inspect the repository first, implement only the requested scope, keep tests passing, and avoid unsafe defaults.

Primary goals:

- preserve existing behavior
- add missing modules incrementally
- keep backend/frontend/CI/Docker working
- maintain strict safety gates
- use mocks/adapters for unavailable external providers
- never commit or expose secrets

---

## 2. Repository Map

Common paths:

```text
.
├── AGENTS.md
├── README.md
├── .env.example
├── .github/workflows/
├── .codex/cloud/
├── docs/prompt/
├── scripts/
├── backend/
├── frontend/
├── infra/docker/
└── config/ecc/
```

Important files:

```text
.codex/cloud/README.md
.codex/cloud/general-custom-instructions.md
.codex/cloud/setup.sh
.codex/cloud/maintenance.sh
.codex/cloud/repair-backend-deps.sh
.codex/cloud/env.safe.example

scripts/run-prompt-phases.sh

backend/pyproject.toml
backend/requirements.txt
backend/app/main.py
backend/app/core/
backend/app/api/
backend/app/tests/

frontend/package.json
frontend/.npmrc
frontend/src/

infra/docker/backend.Dockerfile
infra/docker/frontend.Dockerfile
```

Do not assume every phase module already exists. The prompt files describe desired target modules, but the current repo may be partially implemented. Add safe compatibility shims when previous phase dependencies are missing.

---

## 3. Phase Prompt System

Phase prompts live in:

```text
docs/prompt/
```

Canonical integrated prompt set:

```text
phase01.prompt
phase02.prompt
phase03.prompt
phase04.prompt
phase05.prompt
phase06.prompt
phase07.prompt
phase08.prompt
phase09.prompt
phase10.prompt
phase11.prompt
phase12.prompt
phase13.prompt
phase14.prompt
phase15.prompt
phase16.prompt
phase17.prompt
phase18.prompt
phase19.prompt
phase20.prompt
phase21.prompt
phase22.prompt
phase23.prompt
phase24.prompt
phase25.prompt
phase26.prompt
phase27.prompt
phase28.prompt
phase29.prompt
phase30.prompt
phase31.prompt
phase32.prompt
```

Execution policy:

1. Run one phase per task unless the user explicitly asks for batch execution.
2. Read only the requested phase prompt and relevant existing code.
3. Do not implement later phases early.
4. Do not rewrite earlier phases from scratch.
5. If an earlier dependency is missing, add a minimal shim and document it.
6. Run validation after each phase.
7. Commit one phase at a time when commit access is available.

Phase runner:

```bash
FROM=1 TO=1 ./scripts/run-prompt-phases.sh
FROM=2 TO=2 ./scripts/run-prompt-phases.sh
FROM=1 TO=32 ./scripts/run-prompt-phases.sh
```

Recommended batch chunks when explicitly requested:

```bash
FROM=1 TO=5 ./scripts/run-prompt-phases.sh
FROM=6 TO=10 ./scripts/run-prompt-phases.sh
FROM=11 TO=15 ./scripts/run-prompt-phases.sh
FROM=16 TO=20 ./scripts/run-prompt-phases.sh
FROM=21 TO=25 ./scripts/run-prompt-phases.sh
FROM=26 TO=32 ./scripts/run-prompt-phases.sh
```

---

## 4. Hard Safety Invariants

Never enable by default:

- live trading
- real broker order execution
- real IoT power actions
- real social posting
- secret export
- secret inclusion in bundles
- real infrastructure mutation
- real update apply
- real rollback execution
- raw shell relay
- unreviewed plugin execution
- plugin secret access
- plugin unrestricted external network access
- destructive automation

Never bypass:

- Guardian risk checks
- drawdown guard checks
- kill switch checks
- halt flag checks
- content approval checks
- RBAC
- tenant isolation
- audit logging
- policy engine checks
- certification gates when present
- attestation gates when present
- backup/readiness checks before real mutation

External/customer-impacting actions must default to one of:

- dry-run
- read-only
- mock mode
- simulation mode
- approval-gated mode

Any real mutation must require:

1. admin permission
2. explicit typed confirmation
3. passing validation/preflight checks
4. audit event
5. rollback or recovery plan where applicable

---

## 5. Secret Handling

Never commit:

- `.env`
- API keys
- provider tokens
- private keys
- SSH keys
- broker credentials
- Stripe secrets
- Cloudflare tokens
- webhook secrets
- database URLs with passwords
- real customer data

Allowed examples:

- `.env.example`
- `env.safe.example`
- placeholder values with empty strings
- fake documented examples clearly marked as placeholders

Do not add fake-looking secrets that match scanner patterns. Prefer empty values:

```env
OPENAI_API_KEY=
CLOUDFLARE_API_TOKEN=
STRIPE_SECRET_KEY=
```

Generated artifacts must exclude secrets by default, including:

- support bundles
- deployment packs
- air-gap bundles
- audit exports
- data-plane exports
- RAG context outputs
- release dossiers
- board packs

---

## 6. Setup and Dependency Policy

Use Codex Cloud setup helpers when available:

```bash
bash .codex/cloud/setup.sh
```

Backend dependency repair:

```bash
bash .codex/cloud/repair-backend-deps.sh
```

Frontend dependency policy:

```bash
cd frontend
npm install --legacy-peer-deps --no-audit --fund=false
```

Do not remove `frontend/.npmrc` unless the frontend lockfile and Vite/plugin dependency graph are intentionally repaired. Current frontend setup tolerates peer dependency drift using `legacy-peer-deps`.

Healthcheck:

```bash
bash .codex/healthcheck.sh
```

Maintenance:

```bash
bash .codex/cloud/maintenance.sh
```

---

## 7. Verification Commands

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm install --legacy-peer-deps --no-audit --fund=false
npm test -- --run
npm run build
```

Full validation override for the phase runner:

```bash
VALIDATE_CMD='if [ -d backend ]; then cd backend && pytest && cd ..; fi; if [ -d frontend ]; then cd frontend && npm install --legacy-peer-deps --no-audit --fund=false && npm test -- --run && npm run build && cd ..; fi' FROM=1 TO=32 ./scripts/run-prompt-phases.sh
```

If validation fails:

1. Read the exact error.
2. Fix the root cause.
3. Rerun the same command.
4. Do not delete tests to make CI pass.
5. Do not weaken safety tests.
6. Do not hide errors by making required checks non-blocking unless the workflow already defines them as advisory.

---

## 8. Backend Guide

Backend stack:

- Python 3.11+
- FastAPI
- Pydantic v2
- pydantic-settings
- SQLModel / SQLAlchemy where persistence exists
- Alembic where migrations exist
- pytest
- httpx for API tests

Dependency manifests:

```text
backend/pyproject.toml
backend/requirements.txt
```

`backend/requirements.txt` exists for CI/Docker compatibility. Keep it in sync when adding backend runtime dependencies.

Backend conventions:

1. Use typed Python where practical.
2. Prefer small services and adapter classes over monolithic endpoints.
3. Put API routers under `backend/app/api/`.
4. Put domain logic under `backend/app/<domain>/`.
5. Use existing response helpers when available.
6. Use dependency injection for provider adapters.
7. Keep provider integrations mock-safe by default.
8. Make missing optional providers degrade gracefully.
9. Emit events/audit records for sensitive actions when those systems exist.
10. Keep tests deterministic and offline.

Standard API response shape for new APIs:

Success:

```json
{
  "ok": true,
  "data": {},
  "error": null,
  "timestamp": "ISO_DATE"
}
```

Error:

```json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  },
  "timestamp": "ISO_DATE"
}
```

Use existing helpers, usually under `backend/app/core/responses.py`, when present.

---

## 9. Frontend Guide

Frontend stack:

- React
- Vite
- TypeScript
- Tailwind where present
- Vitest / React Testing Library where present

Frontend commands:

```bash
cd frontend
npm install --legacy-peer-deps --no-audit --fund=false
npm test -- --run
npm run build
```

Frontend conventions:

1. Never expose secrets through `VITE_*` variables.
2. Use mock fallback when backend modules are missing or disabled.
3. Show dry-run/read-only/approval-required states clearly.
4. Disable or hide real mutation buttons unless enabled and authorized.
5. Add route/sidebar entries only when the page exists.
6. Keep TypeScript types aligned with backend API response shapes.
7. Prefer small page-level components and reusable domain components.
8. Build must pass with `npm run build`.
9. Tests must tolerate no-test phase scaffolding where appropriate.
10. Do not require live external provider credentials in frontend tests.

---

## 10. CI and Docker Guide

Workflows live under:

```text
.github/workflows/
```

Current CI policy:

- backend tests install from `backend/pyproject.toml` first, with `backend/requirements.txt` compatibility when needed
- frontend installs use `npm install --legacy-peer-deps --no-audit --fund=false`
- security audits may be non-blocking only when the workflow explicitly marks them non-blocking
- secret pattern scans must remain blocking for real secret patterns

Dockerfiles:

```text
infra/docker/backend.Dockerfile
infra/docker/frontend.Dockerfile
```

Docker rules:

1. Keep images buildable without real provider secrets.
2. Do not bake secrets into images.
3. Keep frontend Docker install aligned with `frontend/.npmrc` and current npm install policy.
4. Keep backend Docker install aligned with `backend/requirements.txt`.
5. Healthchecks should verify local service availability only.

---

## 11. Phase-Specific Expectations

Phase 01:

- Foundation only.
- Janie Server, Agent Runtime, CEO/Janie agents, mock AI fallback, event bus, health/agents/logs APIs.
- Do not implement trading, dashboard, scheduler, IoT, or live execution.

Phase 02:

- Trading Core only.
- XAU Scanner, MT5 adapter shell, Funnel Filter 21/10/3, signal validation, dry-run execution.
- Live trading remains blocked by default.
- No financial advice.

Phase 03:

- Risk system, Guardian, drawdown guard, kill switch, halt flag.
- No unsafe auto-trading by default.

Phase 04:

- Scheduler, IoT adapter shell, Windows service/NSSM guidance.
- Real IoT remains blocked by default.

Phase 05:

- Backtesting and optimization.
- Backtesting only; no live execution.

Phase 06:

- Content pipeline.
- Auto-post remains disabled by default.

Phase 07:

- Dashboard integration.
- No secret exposure in frontend.

Phase 08–20:

- Preserve previous modules and extend according to prompt files.
- Add safety gates, tests, docs, RBAC, tenancy, and audit where requested.

Phase 21–32:

- Enterprise endgame prompt set.
- Governance, certification, auditor portal, deployment packs, managed updates, fleet relay, AI Ops, data plane, marketplace, endgame release, sovereign cloud, and security ops must remain dry-run, read-only, mock, or approval-gated by default.

---

## 12. External Provider Policy

Use mocks, adapters, and dependency injection for:

- Claude/OpenAI
- MT5 / broker integrations
- Tapo / IoT integrations
- social media APIs
- image generation APIs
- Stripe
- Cloudflare
- HeyGen
- GitHub
- Slack
- email/SMTP
- cloud providers

Tests must not require real credentials or network access.

Provider adapters must fail safely when:

- dependency is not installed
- credentials are missing
- provider is disabled
- `DRY_RUN=true`
- approval is missing

---

## 13. Output / Final Report Format

Every implementation task should end with:

1. Repository inspection summary
2. Phase or task implemented
3. Files changed
4. Tests added or updated
5. Validation commands run and results
6. Safety checklist
7. Known limitations
8. Next handoff notes

Do not paste unnecessary giant file dumps when files are already written to the repository.

---

## 14. Do Not Do

Do not:

- delete tests to make CI pass
- weaken safety tests
- commit `.env` files
- commit provider tokens
- add fake secrets
- put secrets into prompt files
- enable real trading by default
- enable real IoT by default
- enable real social posting by default
- add destructive scripts without confirmations
- make external network calls mandatory for tests
- assume unavailable paid APIs are present
- require real broker credentials for tests
- require real social provider credentials for tests
- require real cloud credentials for tests
- require real Stripe credentials for tests
- require real Cloudflare credentials for tests
- require real HeyGen credentials for tests
- require real AI provider credentials for tests

---

## 15. ECC / Codex CLI Integration

This repository may also include ECC support for Codex CLI.

### Model Recommendations

| Task Type | Recommended Model |
|-----------|------------------|
| Routine coding, tests, formatting | GPT 5.4 |
| Complex features, architecture | GPT 5.4 |
| Debugging, refactoring | GPT 5.4 |
| Security review | GPT 5.4 |

### Skills Discovery

Skills are expected under `.agents/skills/` with:

- `SKILL.md`
- `agents/openai.yaml`

This environment may mount `.agents` as read-only, so ECC skill assets may be indexed in:

```text
config/ecc/skills-index.txt
```

### MCP Servers

Treat the following as ECC baseline references when present:

```text
config/ecc/codex/config.toml
```

Managed ECC MCP set:

- `supabase`
- `playwright`
- `context7`
- `exa`
- `github`
- `memory`
- `sequential-thinking`

Use this helper when present:

```bash
scripts/sync-ecc-to-codex.sh
```

### Multi-Agent Support

ECC sample role configs may exist under:

```text
config/ecc/codex/agents/explorer.toml
config/ecc/codex/agents/reviewer.toml
config/ecc/codex/agents/docs-researcher.toml
```

### External Action Boundaries

Treat networked tools as read-only unless explicit user approval is provided for publish, push, post, deploy, payment, credential, or destructive changes.

---

## 16. Final Rule

For every task: inspect, implement, test, document, preserve safety, and report clearly.

### Realtime Layer
- Endpoint: `/api/realtime/ws` with structured/sanitized event envelopes only.
- Notification center and live feeds consume websocket events safely.
- Frontend auto-fallback: simulated realtime mode when WS unavailable.
- Diagnostics: websocket status and last event health indicators.
- Safety: no live execution toggles, no token/secret emission in realtime payloads.

## Phase 7.10 Notes
- Collaboration layer is tenant-scoped and dry-run safe.
