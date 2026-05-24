# KILL_SWITCH

## Purpose
Operate halt and kill-switch safely.

## Prerequisites
- Admin role for emergency lock and reset

## Commands
```bash
# Emergency lock halt
POST /api/risk/emergency-halt

# Resume normal halt
POST /api/risk/resume

# Reset locked kill-switch
POST /api/risk/kill-switch-reset
```

## Expected output
- Emergency halt sets locked flag.
- Reset clears locked halt with audit trail.

## Failure handling
- If reset denied, verify role and lock status.

## Rollback steps
- Keep system halted and perform manual intervention.

## Safety notes
- Emergency halt is intentionally hard to bypass.
