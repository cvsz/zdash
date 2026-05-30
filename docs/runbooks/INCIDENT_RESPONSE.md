# Incident Response Runbook

> Note: This file is maintained at `docs/runbooks/incident-response-runbook.md` (preferred). This copy exists for backward compatibility.

## Incident classes

| Class | Examples | Response |
|-------|----------|----------|
| SECURITY | Breach, unauthorized access, secret leak | Emergency halt + rotate secrets |
| TRADING | Unexpected trade, strategy failure | Kill switch + halt |
| PLATFORM | Service down, high error rate | Rollback + restart |
| DATA | Data loss, corruption, leak | Restore from backup |
| INTEGRATION | Provider failure, rate limit | Circuit break + failover |

## Commands

```bash
# Emergency halt
curl -X POST http://localhost:8005/api/risk/emergency-halt \
  -H 'Authorization: Bearer <admin-token>' \
  -H 'Content-Type: application/json' \
  -d '{"reason":"<incident-description>"}'

# Kill switch (if API unavailable, stop at orchestrator level)
docker compose -f docker-compose.prod.yml stop
```

## Prerequisites

- Admin credentials
- Access to logs and metrics

## Expected output

- Halt state locked and execution blocked.

## Response phases

1. **Containment**: Emergency halt or stop services.
2. **Investigation**: Check logs, audit trail, metrics.
3. **Recovery**: Rollback or restore from backup.
4. **Post-incident**: RCA, update runbooks, add tests.

## Failure handling

- If API unavailable, stop backend at orchestrator level.

## Rollback steps

- Follow `docs/runbooks/rollback-runbook.md` for rollback.
- After RCA, use kill-switch reset endpoint with admin approval.

## Safety notes

- Do not re-enable live mode before RCA and sign-off.
- Preserve all logs and evidence for forensics.
- Rotate any exposed secrets.
