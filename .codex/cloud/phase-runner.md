# zDash Codex Cloud Phase Runner

Use these prompt templates directly in Codex Cloud tasks.

## Run a specific phase (canonical prompt file)

```text
Read docs/prompt/phase08.prompt.

Implement Phase 08 only.

Requirements:
- inspect repository first
- keep behavior backward-compatible
- preserve all safety defaults
- run backend and frontend validation
- return concise implementation report
```

## Run a specific codex-run prompt

```text
Read docs/prompt/codex-runs/phase08.5.prompt and execute it exactly.
Keep scope to Phase 08.5 only.
Validate backend and frontend before committing.
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

Never use `localhost:8000`; backend port is `8005`.
