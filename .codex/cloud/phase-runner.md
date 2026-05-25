# zDash Codex Cloud Phase Runner

Use these prompts as Codex Cloud tasks.

## Run a specific phase

```text
Read docs/prompt/phase24.prompt.

Implement Phase 24 only.

Requirements:
- Inspect repo first.
- Preserve existing behavior.
- Add safe shims for missing modules.
- Keep all safety defaults locked.
- Add backend/frontend tests.
- Update README and .env.example.
- Run backend and frontend checks.

Return:
1. Inspection summary
2. Files changed
3. Tests run
4. Safety checklist
5. Known limitations
6. Next phase handoff
```


## Run all remaining phases (sequential)

```text
Read .codex/cloud/README.md first, then run the remaining phase prompts in order:
phase24.prompt → phase25.prompt → phase26.prompt → phase27.prompt → phase28.prompt → phase29.prompt → phase30.prompt → phase31.prompt → phase32.prompt.

Implement one phase at a time and keep behavior backward-compatible between phases.
After each phase:
- run backend and frontend checks
- commit with a small reviewable message
- continue to the next phase only if checks pass

After the last phase:
- run full backend/frontend verification again
- prepare a summary covering all phases
- if user approval explicitly allows it, push the branch

Safety invariants stay mandatory for every phase:
- no live trading by default
- no real IoT by default
- no real social posting by default
- no secret export by default
- no RBAC bypass
- no tenant isolation bypass
- dry-run/read-only/approval-gated defaults
```

## Generic phase prompt

```text
Read docs/prompt/phase{{PHASE_NUMBER}}.prompt.

Implement Phase {{PHASE_NUMBER}} only.

Do not implement later phases.

Follow all safety invariants:
- no live trading by default
- no real IoT by default
- no real social posting by default
- no secret export by default
- no RBAC bypass
- no tenant isolation bypass
- dry-run/read-only/approval-gated defaults

Run all relevant backend and frontend checks before final response.
```

## Local helper command

After running `.codex/cloud/setup.sh`, the setup script creates:

```bash
bash .codex/run-phase.sh 24
```

This prints the selected prompt file so Codex can use it as task context.

## Recommended phase order

```text
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

## Verification

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
