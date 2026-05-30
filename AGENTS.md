# zDash · Agent Guide

Repository: `cvsz/zdash`

## 1. Mission

Implement zDash phase-by-phase with production quality while preserving safety defaults. Phases live in `docs/prompt/` (phase01–phase32). Inspect the repo first, implement only requested scope, keep tests passing, never commit secrets.

---

## 2. Repository Map

```
backend/          # FastAPI (Python 3.11+, Pydantic v2, SQLModel, Alembic)
frontend/         # React / Vite / TypeScript / Tailwind / Vitest
docs/prompt/      # Phase prompt files (phase01–phase32, agent-roster)
scripts/          # Phase runner, setup, smoke tests
infra/docker/     # backend/frontend/nginx Dockerfiles
.github/workflows/ # CI, security, deploy workflows
```

Key config files: `backend/pyproject.toml`, `backend/requirements.txt`, `frontend/package.json`, `frontend/.npmrc`, `frontend/vite.config.ts`, `frontend/vitest.config.ts`, `Makefile`.

---

## 3. Phase Workflow

Run one phase per task unless asked for batch:

```bash
FROM=1 TO=1 ./scripts/run-prompt-phases.sh
FROM=1 TO=5 ./scripts/run-prompt-phases.sh   # small batch
FROM=1 TO=32 ./scripts/run-prompt-phases.sh   # full run
```

Each phase extends the previous. Add safe shims if earlier dependencies are missing. Do not implement later phases early. Run validation after each phase. Commit one phase at a time.

---

## 4. Safety Invariants

**Never enable by default:** live trading, real broker/IoT/social actions, secret export, infrastructure mutation, raw shell relay, unreviewed plugins, destructive automation.

**Never bypass:** Guardian/risk checks, drawdown/kill-switch/halt flags, content approval, RBAC, tenant isolation, audit logging, policy/certification gates.

**External actions default to:** dry-run, read-only, mock, or approval-gated.

**Real mutations require:** admin permission + typed confirmation + validation preflight + audit event + rollback plan.

---

## 5. Secret Handling

Never commit `.env`, API keys, tokens, private keys, credentials, real customer data. Use `.env.example` with empty placeholder values. Generated artifacts (bundles, packs, exports, dossiers) must exclude secrets by default.

---

## 6. Commands (via Makefile)

Primary validations:

```bash
make validate-fast       # safety scan + lint + backend tests + frontend tests + build
make validate            # validate-fast + Docker + compose check
make golive              # install deps + validate-fast
make safety-scan        # tracked-forbidden + env-check + port-scan + secret-scan
```

Backend:

```bash
make backend-lint        # ruff check app tests
make backend-lint-fix    # ruff check --fix
make backend-test        # pytest -q (with -B flag, no .pyc)
make backend-check       # lint + test
make run-backend         # uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

Frontend:

```bash
make frontend-install    # npm install --legacy-peer-deps --no-audit --fund=false
make frontend-test       # npm test (vitest --run --passWithNoTests)
make frontend-build      # npm run build
make frontend-check      # test + build
make run-frontend        # npm run dev -- --host 0.0.0.0 --port 5173
```

Docker:

```bash
make docker-build        # all images
make compose-up          # local stack
make compose-prod-up     # production stack
```

Release:

```bash
make release-local       # golive + release-notes + artifact
make release-push        # + tag + push (requires CONFIRM_RELEASE=yes)
```

**Ports:** backend `8005`, frontend `5173`, never `8000`. Check live: `curl http://localhost:8005/health`.

---

## 7. Backend Conventions

- Typed Python. Small services/adapter classes > monolithic endpoints.
- Routers under `app/api/`, domain logic under `app/<domain>/`.
- API response shape: `{"ok": bool, "data": {...} | null, "error": {...} | null, "timestamp": "ISO_DATE"}`
- Use helpers from `app/core/responses.py` when present.
- Provider integrations: dependency-injected, mock-safe by default, degrade gracefully when missing.
- Tests: deterministic, offline, `httpx` for API tests. Pytest options: `testpaths = ["tests", "app/tests"]`, warning filter for passlib `crypt`.
- `backend/requirements.txt` must stay in sync with `pyproject.toml` for CI/Docker.

---

## 8. Frontend Conventions

- Never expose secrets via `VITE_*` variables.
- Mock fallback when backend is unavailable (`VITE_ENABLE_MOCK_FALLBACK=true`).
- Show dry-run/approval-required states clearly. Disable real mutation buttons unless authorized.
- API client at `frontend/src/api/client.ts`, endpoints at `frontend/src/api/endpoints.ts`, mock data at `frontend/src/api/mockData.ts`.
- Keep TypeScript types aligned with API response shapes.
- `npm test` runs `vitest --run --passWithNoTests`. Do **not** run `npm test -- --run` — Vitest 4.x rejects duplicate `--run`.
- `.npmrc` sets `legacy-peer-deps=true` (do not change while Vite/plugin deps stabilize).

---

## 9. CI / Docker

- `.github/workflows/ci.yml` runs backend tests (ruff + pytest), frontend tests (vitest + build), Docker build.
- Secret pattern scans must remain blocking.
- Docker images: no real secrets baked in. Healthchecks verify local service only.

---

## 10. Phase Scope Summary

| Phase | Focus |
|-------|-------|
| 01 | Foundation: agents, runtime, mock AI, event bus, health APIs |
| 02 | Trading core (sim/dry-run): XAU scanner, MT5 shell, Funnel Filter |
| 03 | Risk: Guardian, drawdown guard, kill switch |
| 04 | Scheduler, IoT shell |
| 05 | Backtesting engine, optimizer |
| 06 | Content pipeline (approval-gated) |
| 07 | Dashboard integration |
| 08–20 | Expansion: persistence, auth/RBAC, audit, compliance, plugins |
| 21–32 | Enterprise: governance, certification, marketplace, sovereign cloud, security ops |

All phases remain dry-run/mock/approval-gated by default.

---

## 11. External Provider Policy

Mock/DI for: Claude/OpenAI, MT5, Tapo/IoT, social APIs, image gen, Stripe, Cloudflare, HeyGen, GitHub, Slack, email, cloud providers. Tests must not require real credentials or network. Providers fail safely when deps missing, creds unset, provider disabled, `DRY_RUN=true`, or approval missing.

---

## 12. Environment Variables

Start from `.env.example`. Key safe defaults:

```env
BACKEND_PORT=8005
DRY_RUN=true
LIVE_TRADING_ACK=false
RISK_GUARDIAN_ENABLED=true
MT5_ENABLED=false
SOCIAL_DRY_RUN=true
SOCIAL_AUTO_POST_ENABLED=false
IOT_DRY_RUN=true
ALLOW_STRATEGY_PROMOTION=false
UPDATE_DRY_RUN=true
```

Do not commit `.env` or real secrets. Rotate JWT/admin secrets before production.

---

## 13. ECC / Codex CLI

Skills under `.agents/skills/`. MCP set: supabase, playwright, context7, exa, github, memory, sequential-thinking. Vendor configs at `config/ecc/codex/`. Networked tools are read-only unless explicit approval for publish/push/post/credential changes.
