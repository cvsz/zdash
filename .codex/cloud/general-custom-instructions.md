# Codex Cloud · General Custom Instructions

Paste the text block below into Codex Cloud General Custom Instructions for repository `cvsz/zdash`.

```text
You are working in repository:

cvsz/zdash

Project:

⬡ zDash · FULL SYSTEM BLUEPRINT v2.0

Primary objective:
Implement the requested zDash phase safely, incrementally, and with production-grade code quality.

============================================================
REPOSITORY EXECUTION POLICY
============================================================

1. Always inspect the repository before coding.
2. Implement only the phase explicitly requested by the user or task prompt.
3. Do not implement later phases unless the user explicitly requests a batch run.
4. Do not rebuild existing modules from scratch.
5. Do not remove existing behavior unless the phase explicitly requires a migration.
6. If an expected previous phase module is missing, create a safe compatibility shim or minimal adapter instead of breaking the build.
7. Prefer small, reviewable commits.
8. Keep backend and frontend tests passing.
9. Update README, docs, tests, and `.env.example` when adding features.
10. Never commit secrets.
11. Never expose secrets in frontend code, logs, docs, prompts, support bundles, deployment packs, air-gap bundles, update plans, diagnostics, generated reports, or generated artifacts.
12. All new APIs must use the standard zDash response shape unless the existing app already defines a different canonical helper.
13. All new data must be tenant-scoped when tenancy/workspaces exist.
14. All sensitive operations must emit events and audit logs when event/audit modules exist.
15. Generated code must be real implementation code, not pseudocode.

============================================================
SAFETY INVARIANTS
============================================================

Never enable by default:

- live trading
- real broker execution
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

Never bypass:

- Guardian risk checks
- drawdown guard / kill switch checks
- content approval checks
- RBAC
- tenant isolation
- audit logging
- policy engine checks
- certification gates when present
- attestation gates when present
- backup/readiness checks before real mutation

All external, remote, cloud, installer, update, support, relay, fleet, marketplace, AI Ops, and automation actions must default to one of:

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

============================================================
TECH STACK ASSUMPTIONS
============================================================

Backend:

- Python 3.11+
- FastAPI
- Pydantic v2
- pydantic-settings
- SQLModel / SQLAlchemy where persistence exists
- Alembic where migrations exist
- pytest
- httpx for API tests

Frontend:

- React
- Vite
- TypeScript
- Tailwind where present
- Vitest / React Testing Library where present

Docker/CI:

- Backend Dockerfile may install from `backend/requirements.txt`.
- Backend package metadata may live in `backend/pyproject.toml`.
- Frontend installs must tolerate the current Vite/plugin dependency state.
- Use `npm install --legacy-peer-deps --no-audit --fund=false` for frontend setup unless the repo lockfile is repaired and CI explicitly changes this policy.

============================================================
CODEX CLOUD SETUP POLICY
============================================================

Before implementation, use the repo setup helpers when available:

```bash
bash .codex/cloud/setup.sh
```

If backend imports fail because dependencies are missing, run:

```bash
bash .codex/cloud/repair-backend-deps.sh
```

If frontend dependency resolution fails, use:

```bash
cd frontend
npm install --legacy-peer-deps --no-audit --fund=false
```

Do not remove `frontend/.npmrc` unless the frontend lockfile and Vite/plugin dependency graph are intentionally repaired.

After setup, run healthcheck when available:

```bash
bash .codex/healthcheck.sh
```

Maintenance check:

```bash
bash .codex/cloud/maintenance.sh
```

============================================================
DEFAULT VERIFICATION COMMANDS
============================================================

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

Full repo helper:

```bash
bash .codex/healthcheck.sh
```

If validation fails:

1. Read the exact failing error.
2. Fix the root cause.
3. Rerun the same command.
4. Do not hide failures by deleting tests or weakening safety checks.
5. Non-blocking audit commands may stay non-blocking only if the workflow already marks them non-blocking.

============================================================
PHASE PROMPT INVENTORY
============================================================

Phase prompts live under:

```text
docs/prompt/
```

Canonical integrated prompt set:

```text
docs/prompt/phase01.prompt
docs/prompt/phase02.prompt
docs/prompt/phase03.prompt
docs/prompt/phase04.prompt
docs/prompt/phase05.prompt
docs/prompt/phase06.prompt
docs/prompt/phase07.prompt
docs/prompt/phase08.prompt
docs/prompt/phase09.prompt
docs/prompt/phase10.prompt
docs/prompt/phase11.prompt
docs/prompt/phase12.prompt
docs/prompt/phase13.prompt
docs/prompt/phase14.prompt
docs/prompt/phase15.prompt
docs/prompt/phase16.prompt
docs/prompt/phase17.prompt
docs/prompt/phase18.prompt
docs/prompt/phase19.prompt
docs/prompt/phase20.prompt
docs/prompt/phase21.prompt
docs/prompt/phase22.prompt
docs/prompt/phase23.prompt
docs/prompt/phase24.prompt
docs/prompt/phase25.prompt
docs/prompt/phase26.prompt
docs/prompt/phase27.prompt
docs/prompt/phase28.prompt
docs/prompt/phase29.prompt
docs/prompt/phase30.prompt
docs/prompt/phase31.prompt
docs/prompt/phase32.prompt
```

Recommended execution order:

phase01.prompt → phase02.prompt → phase03.prompt → phase04.prompt → phase05.prompt → phase06.prompt → phase07.prompt → phase08.prompt → phase09.prompt → phase10.prompt → phase11.prompt → phase12.prompt → phase13.prompt → phase14.prompt → phase15.prompt → phase16.prompt → phase17.prompt → phase18.prompt → phase19.prompt → phase20.prompt → phase21.prompt → phase22.prompt → phase23.prompt → phase24.prompt → phase25.prompt → phase26.prompt → phase27.prompt → phase28.prompt → phase29.prompt → phase30.prompt → phase31.prompt → phase32.prompt

Default mode:

- Run one phase per Codex task.
- Commit one phase at a time.
- Run validation after each phase.
- Continue to the next phase only after checks pass or after the user explicitly approves continuing with known failures.

Batch execution is allowed only when the user explicitly asks for it.

============================================================
PHASE RUNNER COMMANDS
============================================================

Run Phase 1 only:

```bash
FROM=1 TO=1 ./scripts/run-prompt-phases.sh
```

Run Phase 2 only:

```bash
FROM=2 TO=2 ./scripts/run-prompt-phases.sh
```

Run Phase 1 through 32:

```bash
FROM=1 TO=32 ./scripts/run-prompt-phases.sh
```

Recommended batch chunks:

```bash
FROM=1 TO=5 ./scripts/run-prompt-phases.sh
FROM=6 TO=10 ./scripts/run-prompt-phases.sh
FROM=11 TO=15 ./scripts/run-prompt-phases.sh
FROM=16 TO=20 ./scripts/run-prompt-phases.sh
FROM=21 TO=25 ./scripts/run-prompt-phases.sh
FROM=26 TO=32 ./scripts/run-prompt-phases.sh
```

Full validation override:

```bash
VALIDATE_CMD='if [ -d backend ]; then cd backend && pytest && cd ..; fi; if [ -d frontend ]; then cd frontend && npm install --legacy-peer-deps --no-audit --fund=false && npm test -- --run && npm run build && cd ..; fi' FROM=1 TO=32 ./scripts/run-prompt-phases.sh
```

============================================================
IMPLEMENTATION FORMAT FOR EVERY PHASE
============================================================

Return a final implementation report with:

1. Repository inspection summary
2. Phase implemented
3. Folder tree changes
4. New backend files
5. New frontend files
6. Patched existing files
7. Tests added or updated
8. `.env.example` updates
9. README/docs updates
10. API examples
11. Run instructions
12. Test instructions
13. Safety checklist
14. Acceptance checklist
15. Validation commands run with results
16. Known limitations
17. Next phase handoff notes

When code is changed, include concise commit-ready summary. Do not paste unnecessary giant file dumps if files are already written to the repo.

============================================================
STANDARD API RESPONSE SHAPE
============================================================

Prefer this response shape for new APIs:

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

============================================================
PHASE-SPECIFIC EXPECTATIONS
============================================================

Phase 01:
- Foundation only.
- Janie Server, Agent Runtime, CEO/Janie agents, mock AI fallback, event bus, health/agents/logs APIs.
- Do not implement trading, dashboard, scheduler, IoT, or live execution.

Phase 02:
- Trading Core only.
- XAU Scanner, MT5 adapter shell, Funnel Filter 21/10/3, signal validation, dry-run execution.
- Live trading remains blocked by default.

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
- Governance, certification, auditor portal, deployment packs, managed updates, fleet relay, AI Ops, data plane, marketplace, endgame release, sovereign cloud, and security ops must all remain dry-run/read-only/approval-gated by default.

============================================================
DO NOT DO
============================================================

Do not:

- delete tests to make CI pass
- weaken safety tests
- commit `.env` files
- commit provider tokens
- add fake secrets
- put secrets into prompt files
- enable real trading or real IoT by default
- add destructive scripts without confirmations
- make external network actions mandatory for tests
- assume unavailable paid APIs are present
- require real broker, social, cloud, Stripe, Cloudflare, HeyGen, or AI provider credentials for tests

Use mocks, adapters, and dependency injection for provider integrations.

============================================================
CURRENT REPO CI / SETUP NOTES
============================================================

Known setup policies in this repo:

- `backend/requirements.txt` exists for CI/Docker compatibility.
- `backend/pyproject.toml` contains backend package metadata.
- `.codex/cloud/repair-backend-deps.sh` repairs backend runtime dependency drift.
- `frontend/.npmrc` sets `legacy-peer-deps=true`.
- Frontend setup should use `npm install --legacy-peer-deps --no-audit --fund=false`.
- CI workflows should not use strict `npm ci` unless the lockfile has been intentionally repaired.

If CI fails, inspect the specific workflow/job logs first. Fix root causes in source/config. Do not guess.

============================================================
FINAL RULE
============================================================

For every task: inspect, implement, test, document, preserve safety, and report clearly.
```
