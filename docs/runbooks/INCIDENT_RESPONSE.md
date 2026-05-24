# INCIDENT_RESPONSE

## Purpose
Respond to trading/platform/security incidents.

## Prerequisites
- Admin credentials
- Access to logs and metrics

## Commands
```bash
curl -X POST http://<host>/api/risk/emergency-halt -H 'Authorization: Bearer <admin-token>' -H 'Content-Type: application/json' -d '{"reason":"incident"}'
```

## Expected output
- Halt state locked and execution blocked.

## Failure handling
- If API unavailable, stop backend at orchestrator level.

## Rollback steps
- After RCA, use kill-switch reset endpoint with admin approval.

## Safety notes
- Do not re-enable live mode before RCA and sign-off.
