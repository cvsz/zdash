# Live Trading Safety

## Default posture
- Live trading is disabled by default.
- `DRY_RUN=true` is the default baseline.

## Required gates for live execution
All gates must be true:
1. `DRY_RUN=false`
2. `LIVE_TRADING_ACK=true`
3. `RISK_GUARDIAN_ENABLED=true`
4. `ADMIN_APPROVED_LIVE_MODE=true`
5. Latest manual approval exists via `POST /api/trading/live-mode/confirm` with `approved=true`

## Hard stops
- Emergency halt (`POST /api/risk/emergency-halt`) sets a locked halt state.
- Locked halt cannot be resumed by normal flow.
- Kill-switch reset requires admin and explicit reason.

## Operational recommendations
- Keep `DRY_RUN=true` in dev/staging.
- Require dual-control change management for production gate toggles.
- Monitor audit logs and `/metrics` before enabling live mode.
