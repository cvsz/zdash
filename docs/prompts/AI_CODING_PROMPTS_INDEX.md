# zDash AI Coding Prompts Index

Use this index to choose the correct zDash AI coding prompt for Codex, DeepSeek V4 Flash Free, or any fast/free coding model with limited context.

## Core execution rules

- Repository: `cvsz/zdash`.
- Inspect before editing.
- Do not rebuild from scratch.
- Preserve existing architecture and working tests.
- Backend port is `8005`; do not introduce `localhost:8000` or `BACKEND_PORT=8000` in tracked runtime/source files.
- Do not commit `.env`, tokens, GPG passphrases, private keys, local agent folders, caches, or Codex run artifacts.
- `docs/prompts/codex-runs/` is local-only and must remain untracked.
- Trading, AI Trader, and strategy execution remain simulation-only / dry-run only.
- Keep live trading disabled.
- Run validation before reporting completion.

## Master prompts

| Prompt | Purpose |
|---|---|
| `docs/prompts/phase33-ai-trader.prompt` | Phase 33 AI Trader Simulation Layer. |
| `docs/prompts/phase34-ai-trader-master-meta-mega.prompt` | Phase 34 AI Trader Control Plane. |
| `docs/prompts/phase35-master-meta-final-release.prompt` | Phase 35 master final release prompt with DeepSeek V4 Flash Free split workflow. |

## Phase 35 split prompts

Use these when the full Phase 35 prompt is too large for the active model.

| Pass | Prompt file | Scope |
|---|---|---|
| 35.1 | `docs/prompts/phase35.1-backend-release-hardening.prompt` | Backend release hardening, RBAC, safety config, API checks, backend tests. |
| 35.2 | `docs/prompts/phase35.2-ai-trader-final-polish.prompt` | AI Trader simulation-only final polish, API/UI/tests/docs. |
| 35.3 | `docs/prompts/phase35.3-frontend-dashboard-ui-polish.prompt` | Frontend dashboard/UI/UX polish and frontend validation. |
| 35.4 | `docs/prompts/phase35.4-docs-runbooks-api-examples.prompt` | Docs, runbooks, README, API examples, troubleshooting. |
| 35.5 | `docs/prompts/phase35.5-makefile-ci-maintenance-validation.prompt` | Makefile, CI, maintenance, safety-scan, full validation. |
| 35.6 | `docs/prompts/phase35.6-final-report-release-handoff.prompt` | Final report and release handoff. |

## Recommended DeepSeek V4 Flash Free command flow

Run one pass at a time:

```bash
cd ~/zdash
codex "$(cat docs/prompts/phase35.1-backend-release-hardening.prompt)"
```

Then continue:

```bash
codex "$(cat docs/prompts/phase35.2-ai-trader-final-polish.prompt)"
codex "$(cat docs/prompts/phase35.3-frontend-dashboard-ui-polish.prompt)"
codex "$(cat docs/prompts/phase35.4-docs-runbooks-api-examples.prompt)"
codex "$(cat docs/prompts/phase35.5-makefile-ci-maintenance-validation.prompt)"
codex "$(cat docs/prompts/phase35.6-final-report-release-handoff.prompt)"
```

If shell prompt length is unstable, pipe the file:

```bash
cat docs/prompts/phase35.1-backend-release-hardening.prompt | codex
```

## Validation checklist

Before marking any pass complete:

```bash
git status --short
make safety-scan
```

Fast validation:

```bash
APP_ENV=development \
DATABASE_URL=sqlite:///./zdash_test.db \
PRODUCTION_SAFETY_LOCK=true \
DRY_RUN=true \
LIVE_TRADING_ACK=false \
make validate-fast
```

Full validation before release:

```bash
APP_ENV=development \
DATABASE_URL=sqlite:///./zdash_test.db \
PRODUCTION_SAFETY_LOCK=true \
DRY_RUN=true \
LIVE_TRADING_ACK=false \
make validate
```

## Known non-blocking warnings

These are not blockers if final summaries pass:

- `passlib` dependency may emit Python `crypt` deprecation warning from `.venv`.
- React `act(...)` warnings may appear in existing hook tests.
- React Router future flag warnings may appear.
- ErrorBoundary tests intentionally throw `Error: fail` to verify fallback rendering.
- Vite may warn about chunk size.

## Blocking failures

Treat these as blockers:

- backend ruff failure
- pytest failed tests
- frontend failed tests
- npm build failure
- make safety-scan failure
- tracked `.env` or secret-like values
- tracked `docs/prompts/codex-runs/`
- runtime/source references to `localhost:8000` or `BACKEND_PORT=8000`
- live trading enabled
- broker execution added
