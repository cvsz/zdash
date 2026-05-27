# zDash Codex Cloud Phase Runner

Use these prompt templates directly in Codex Cloud tasks.

Current baseline:

```text
cvsz/zdash main = Phase 01-08 plus Phase 7.10 collaboration/federation foundation.
Cloudflare operator = cvsz/zeaz-platform.
Support domain = zdash.zeaz.dev.
Backend port = 8005.
Frontend dev port = 5173.
```

## Run a specific phase (canonical prompt file)

```text
Read AGENTS.md, .codex/cloud/README.md, docs/prompt/agent-roster.prompt, and docs/prompt/phaseNN.prompt.

Implement Phase NN only.

Requirements:
- inspect repository first
- keep behavior backward-compatible
- preserve all safety defaults
- keep backend port 8005
- never introduce localhost:8000
- run backend and frontend validation
- run Docker/compose validation when infra changes
- return concise implementation report
```

## Run a specific codex-run prompt

```text
Read docs/prompt/codex-runs/phaseNN.x.prompt and execute it exactly.
Keep scope to that sub-phase only.
Validate backend and frontend before committing.
If infra changes, validate backend/frontend/nginx Docker builds and both compose configs.
```

## Production hardening fix prompt

Use this before the next major phase if not already fixed:

```text
Review current cvsz/zdash main after Phase 08 and Phase 7.10 collaboration merge.

Implement only production-hardening fixes:
1. Ensure backend manifests include psycopg[binary]>=3.2.0 because production compose uses postgresql+psycopg://.
2. Ensure /api/collaboration/ws/collaboration/{workspace_id} validates auth when AUTH_ENABLED=true.
3. Protect workspace federation mutation endpoints with auth/RBAC even though they are mock-only.
4. Add VITE_WS_BASE_URL optional support or derive WS URL from VITE_API_BASE_URL.
5. Add tests for the above.

Rules:
- keep backend port 8005
- never use localhost:8000
- no secrets
- no live trading, real posting, real image APIs, or real IoT actions
- no autopep8 --aggressive

Validation:
cd backend && source .venv/bin/activate && python -m ruff check app tests && python -B -m pytest -q
cd ../frontend && source ~/.nvm/nvm.sh && nvm use 20 && npm test && npm run build
cd .. && docker build -f infra/docker/backend.Dockerfile . && docker build -f infra/docker/frontend.Dockerfile . && docker build -f infra/docker/nginx.Dockerfile . && docker compose config && docker compose -f docker-compose.prod.yml config

Commit:
fix(prod): harden collaboration auth and postgres runtime
```

## Run all integrated phases sequentially

```text
Read .codex/cloud/README.md.
Execute phases in order from docs/prompt/phase01.prompt to docs/prompt/phase32.prompt.

For each phase:
- implement only that phase scope
- run backend/frontend validation
- commit only phase-scoped files
- continue only if validation passes

After final phase:
- run full validation again
- provide combined summary with risks, limitations, and handoff notes
- push only if user explicitly approves
```

## Local helper commands

Print prompt by numeric phase:

```bash
bash .codex/run-phase.sh 08
```

Print prompt by path:

```bash
bash .codex/run-phase.sh docs/prompt/codex-runs/phase08.5.prompt
```

Run maintenance:

```bash
bash .codex/cloud/maintenance.sh
```

## Safety reminder

For every phase keep defaults safe:

- `DRY_RUN=true`
- `LIVE_TRADING_ACK=false`
- `RISK_GUARDIAN_ENABLED=true`
- `MT5_ENABLED=false`
- `SOCIAL_DRY_RUN=true`
- `SOCIAL_APPROVAL_REQUIRED=true`
- `SOCIAL_AUTO_POST_ENABLED=false`
- `IOT_DRY_RUN=true`
- `IOT_REQUIRE_CONFIRMATION=true`
- `ALLOW_STRATEGY_PROMOTION=false`
- `PRODUCTION_SAFETY_LOCK=true`

Never use `localhost:8000`; backend port is `8005`.
Never commit `.env`, tokens, private keys, Cloudflare tokens, tunnel tokens, or local credentials.
Cloudflare edge/operator changes belong in `cvsz/zeaz-platform`, not `cvsz/zdash`.
