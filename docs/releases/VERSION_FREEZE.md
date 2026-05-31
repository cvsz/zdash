# Version Freeze

## Version

```
0.42.0-rc1
```

## Date

2026-05-31

## Release Status

**GO** — all P0 items closed, validation captured, rollback documented, operator handoff ready.

## Safety Status

**LOCKED** — all safety invariants verified:

| Lock | Status |
|------|--------|
| DRY_RUN=true | LOCKED |
| LIVE_TRADING_ACK=false | LOCKED |
| MT5_ENABLED=false | LOCKED |
| PRODUCTION_ALLOW_LIVE_ACTIONS=false | LOCKED |
| RISK_GUARDIAN_ENABLED=true | LOCKED |

## Validation Commands

```bash
make validate-fast          # safety scan + backend tests + frontend tests + build
make phase39-validate       # production dry-run validation
make phase40-validate       # go-live rehearsal validation
make phase41-validate       # release automation validation
make final-release-check    # final public release verification
make phase42-validate       # full validation chain
```

## Rollback Reference

See `docs/runbooks/ROLLBACK_RUNBOOK.md`

## Tag Command

```bash
git tag -a v0.42.0-rc1 -m "zDash v0.42.0-rc1 final public release candidate"
```

## Release Command

```bash
CONFIRM_RELEASE=yes make release-push
CONFIRM_RELEASE=yes make gh-release
```
