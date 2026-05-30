# zDash AI Coding Prompts Index

Use this index to select the correct Codex/new-chat prompt for zDash work. Keep execution phase-scoped, validate after every phase, and never bypass safety policies.

## Core rules for every prompt

- Repository: `cvsz/zdash`.
- Inspect before editing.
- Do not rebuild from scratch.
- Preserve existing architecture and working tests.
- Backend port is `8005`; do not introduce `localhost:8000`.
- Do not commit `.env`, tokens, GPG passphrases, private keys, local agent folders, caches, or Codex run artifacts.
- `docs/prompt/codex-runs/` is local-only and must remain untracked.
- Trading, AI Trader, and strategy execution are simulation-only unless a future explicit safety-approved phase says otherwise.
- Keep live trading disabled.
- Use dry-run/paper-trading paths only.
- Run validation before reporting completion.

## Current prompt files

| Prompt | Purpose |
|---|---|
| `docs/prompt/phase33-ai-trader.prompt` | Phase 33 AI Trader Simulation Layer. |
| `docs/prompt/phase34-ai-trader-master-meta-mega.prompt` | Phase 34 AI Trader Control Plane. |
| `docs/prompt/phase35-master-meta-final-release.prompt` | Phase 35 full final release candidate polish. |

## Recommended new-chat sequence

### 1. Repo recovery / sync

Use when local git is dirty, pull fails, or prompt artifacts are tracked by mistake.

```text
You are working in cvsz/zdash. First inspect git status, current branch, and recent commits. Resolve local/remote divergence safely. Do not discard work without creating a backup branch or stash. Ensure docs/prompt/codex-runs/ is ignored and untracked. Run make safety-scan. Report exact commands and results.
```

### 2. Fast validation

Use after any small patch.

```text
Run zDash fast validation only. Use development/test-safe env overrides. Do not change code unless validation fails. If validation fails, fix the smallest safe issue and rerun.

Commands:
APP_ENV=development \
DATABASE_URL=sqlite:///./zdash_test.db \
PRODUCTION_SAFETY_LOCK=true \
DRY_RUN=true \
LIVE_TRADING_ACK=false \
make validate-fast
```

### 3. Full validation

Use before push/release.

```text
Run zDash full validation. Preserve safety defaults. If Docker is unavailable, report that clearly and complete non-Docker validation. Do not commit secrets or local-only files.

Commands:
APP_ENV=development \
DATABASE_URL=sqlite:///./zdash_test.db \
PRODUCTION_SAFETY_LOCK=true \
DRY_RUN=true \
LIVE_TRADING_ACK=false \
make validate
```

### 4. AI Trader feature patch

Use for AI Trader only.

```text
Execute only AI Trader simulation changes in cvsz/zdash. Do not enable live trading. Do not add broker execution. Do not bypass TradingService, SignalValidationService, ExecutionEngine, Guardian, RBAC, audit/event logging, or dry-run mode. All API/UI execution must be simulation-only and force dry_run=true. Run backend and frontend tests relevant to AI Trader, then run make validate-fast.
```

### 5. Frontend dashboard polish

Use for UI/UX only.

```text
Execute only frontend dashboard/UI polish for cvsz/zdash. Preserve existing routes and API contracts. Improve empty/loading/error states, safety banners, button labels, and responsive layout. Do not add new dependencies unless unavoidable. Run npm test and npm run build.
```

### 6. Backend API hardening

Use for backend only.

```text
Execute only backend API hardening for cvsz/zdash. Verify router registration, response envelopes, auth/RBAC, tenancy isolation, dry-run defaults, safety lock behavior, and audit/event logging. Do not change frontend unless required by a backend contract fix. Run python -m ruff check app tests and python -B -m pytest -q.
```

### 7. Docs and release notes

Use for docs-only work.

```text
Update zDash docs only. Add or improve README sections, architecture docs, API examples, runbooks, and troubleshooting notes. Use backend port 8005. Do not edit source code. Do not commit local-only Codex run files. Run markdown-safe checks if available and make safety-scan.
```

## Phase 35 execution prompt

Use `docs/prompt/phase35-master-meta-final-release.prompt` when the goal is full final release readiness across backend, frontend, docs, validation, and safety.

Do not paste every old phase prompt into one Codex run. Run Phase 35 as the final release coordinator, then create smaller follow-up prompts only for specific failures.

## Validation checklist

Before marking any phase complete:

```bash
git status --short
make safety-scan
APP_ENV=development \
DATABASE_URL=sqlite:///./zdash_test.db \
PRODUCTION_SAFETY_LOCK=true \
DRY_RUN=true \
LIVE_TRADING_ACK=false \
make validate-fast
```

Before release:

```bash
APP_ENV=development \
DATABASE_URL=sqlite:///./zdash_test.db \
PRODUCTION_SAFETY_LOCK=true \
DRY_RUN=true \
LIVE_TRADING_ACK=false \
make validate
```

## Known non-blocking warnings

- `passlib` dependency may emit Python `crypt` deprecation warning from `.venv`.
- React `act(...)` warnings may appear in existing hook tests.
- ErrorBoundary tests intentionally throw `Error: fail` to verify fallback rendering.

These are not blockers if test summaries pass.
