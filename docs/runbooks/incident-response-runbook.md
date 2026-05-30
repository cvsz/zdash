# Incident Response Runbook

## Incident classes

| Class | Examples | Response |
|-------|----------|----------|
| SECURITY | Breach, unauthorized access, secret leak | Emergency halt + rotate secrets |
| TRADING | Unexpected trade, strategy failure | Kill switch + halt |
| PLATFORM | Service down, high error rate | Rollback + restart |
| DATA | Data loss, corruption, leak | Restore from backup |
| INTEGRATION | Provider failure, rate limit | Circuit break + failover |

## Response phases

### 1. Detection

- Monitoring alerts.
- User report.
- Automated safety check failure.

### 2. Triage

1. Confirm incident class.
2. Assess severity (critical / high / medium / low).
3. Notify on-call engineer.

### 3. Containment

```bash
# Emergency halt (trading/platform incidents)
curl -X POST http://localhost:8005/api/risk/emergency-halt \
  -H 'Authorization: Bearer <admin-token>' \
  -H 'Content-Type: application/json' \
  -d '{"reason":"<incident-description>"}'

# Kill switch (if API unavailable, stop at orchestrator level)
docker compose -f docker-compose.prod.yml stop
```

### 4. Investigation

- Check backend logs: `docker compose logs backend`
- Check nginx logs: `docker compose logs nginx`
- Check database: `docker compose logs postgres`
- Review audit logs: `GET /api/admin/audit-logs`

### 5. Recovery

- Follow `docs/runbooks/rollback-runbook.md` for rollback.
- Restore from backup if data affected.
- Rotate any exposed secrets.

### 6. Post-incident

1. File RCA report.
2. Update runbooks.
3. Add tests to prevent recurrence.
4. Schedule security review if applicable.

## Communication

| Channel | When |
|---------|------|
| Ops channel | Immediate notification |
| Stakeholders | Within 1 hour for critical |
| Customers | After confirmation and mitigation |

## Safety notes

- Do not re-enable live mode before RCA and sign-off.
- Kill-switch reset requires admin approval and explicit reason.
- Preserve all logs and evidence for forensics.
