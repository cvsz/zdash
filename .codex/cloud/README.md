# zDash Codex Cloud Setup Suite

Repository: `cvsz/zdash`

This folder contains copy/paste-ready Codex Cloud setup materials for running zDash phase implementation safely.

OpenAI's Codex help states that Codex is an AI agent for writing, reviewing, and shipping code, and that Codex web requires connecting ChatGPT to GitHub. Business/Enterprise controls include workspace app/plugin controls and RBAC permissions for Codex Cloud access.

## Files

- `general-custom-instructions.md` — paste into Codex Cloud General Custom Instructions.
- `setup.sh` — paste into Codex Cloud Setup Script.
- `maintenance.sh` — paste into Codex Cloud Maintenance Script.
- `AGENTS.template.md` — optional repo-level `AGENTS.md` template.
- `phase-runner.md` — task prompts for running phase prompts.
- `env.safe.example` — safe non-secret environment defaults.

## zDash safety defaults

- Live trading disabled by default.
- Real IoT power actions disabled by default.
- Real social posting disabled by default.
- Secret export disabled by default.
- External/customer-impacting workflows must default to dry-run, read-only, mock, or approval-gated mode.
- Guardian risk checks, content approval, RBAC, tenant isolation, and audit logging must not be bypassed.

## Integrated prompt set

The Codex Cloud suite is integrated for these phase prompt files:

```text
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

## Suggested Codex workflow

1. Configure the Codex Cloud environment using `general-custom-instructions.md`.
2. Paste `setup.sh` into the Setup Script.
3. Paste `maintenance.sh` into the Maintenance Script.
4. Start a Codex task with one phase only, for example:

```text
Read docs/prompt/phase21.prompt.
Implement Phase 21 only.
Run backend and frontend checks.
Return inspection summary, files changed, tests run, safety checklist, limitations, and next handoff.
```

For batch execution, use `.codex/cloud/phase-runner.md` section **Run all integrated phases sequentially** to process phases 21→32 with per-phase checks/commits and an optional push only when explicitly approved by the user.

## Verification commands

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test -- --run
npm run build
```
