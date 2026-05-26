# Codex Cloud · General Custom Instructions

Paste the text block below into Codex Cloud General Custom Instructions for repository `cvsz/zdash`.

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

bash .codex/cloud/setup.sh

If backend imports fail because dependencies are missing, run:

bash .codex/cloud/repair-backend-deps.sh

If frontend dependency resolution fails, use:

cd frontend
npm install --legacy-peer-deps --no-audit --fund=false

Do not remove `frontend/.npmrc` unless the frontend lockfile and Vite/plugin dependency graph are intentionally repaired.

After setup, run healthcheck when available:

bash .codex/healthcheck.sh

Maintenance check:

bash .codex/cloud/maintenance.sh

============================================================
DEFAULT VERIFICATION COMMANDS
============================================================

Backend:

cd backend
pytest

Frontend:

cd frontend
npm install --legacy-peer-deps --no-audit --fund=false
npm test -- --run
npm run build

Full repo helper:

bash .codex/healthcheck.sh

============================================================
PHASE PROMPT INVENTORY
============================================================

Phase prompts live under:

docs/prompt/

Canonical integrated prompt set:

docs/prompt/phase01.prompt
docs/prompt/phase02.prompt
...
docs/prompt/phase32.prompt

Recommended execution order:

phase01.prompt → phase02.prompt → ... → phase32.prompt

============================================================
PHASE RUNNER COMMANDS
============================================================

Run Phase 1 only:

FROM=1 TO=1 ./scripts/run-prompt-phases.sh

Run Phase 2 only:

FROM=2 TO=2 ./scripts/run-prompt-phases.sh

Run Phase 1 through 32:

FROM=1 TO=32 ./scripts/run-prompt-phases.sh

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

============================================================
STANDARD API RESPONSE SHAPE
============================================================

Success:

{
  "ok": true,
  "data": {},
  "error": null,
  "timestamp": "ISO_DATE"
}

Error:

{
  "ok": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  },
  "timestamp": "ISO_DATE"
}

============================================================
PHASE-SPECIFIC EXPECTATIONS
============================================================

Phase 01: Foundation only...
Phase 02: Trading Core only...
Phase 03: Risk system...
Phase 04: Scheduler...
Phase 05: Backtesting...
Phase 06: Content pipeline...
Phase 07: Dashboard...
Phase 08–20: Extend modules...
Phase 21–32: Enterprise endgame...

============================================================
DO NOT DO
============================================================

Do not delete tests...
Do not weaken safety...
Do not commit secrets...
Do not enable real trading...

============================================================
CURRENT REPO CI / SETUP NOTES
============================================================

- `backend/requirements.txt` exists
- `backend/pyproject.toml` contains metadata
- `.codex/cloud/repair-backend-deps.sh` repairs drift
- `frontend/.npmrc` sets legacy-peer-deps
- CI workflows should not use strict `npm ci` unless lockfile repaired

============================================================
FINAL RULE
============================================================

For every task: inspect, implement, test, document, preserve safety, and report clearly.
