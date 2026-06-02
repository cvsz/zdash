# Incident Response Runbook

## Severity Levels

| Severity | Definition | Examples | Response Time | Resolution Target |
|----------|-----------|----------|--------------|-------------------|
| **SEV1** | Critical service outage or data loss affecting all users | Complete backend down, database corruption, security breach | 15 min | < 4 hours |
| **SEV2** | Partial outage or degraded service affecting a subset of users | One API endpoint failing, high latency, feature unavailable | 1 hour | < 8 hours |
| **SEV3** | Minor issue with workaround available | UI bug, non-critical error, documentation issue | 4 hours | < 24 hours |
| **SEV4** | Cosmetic or enhancement request | Styling issue, feature request, minor warning | 1 business day | Next release |

## Incident Classes

| Class | Examples | Initial Response |
|-------|----------|-----------------|
| SECURITY | Breach, unauthorized access, secret leak | Emergency halt + rotate secrets |
| TRADING | Unexpected trade simulation behavior, strategy failure | Kill switch + halt |
| PLATFORM | Service down, high error rate, database failure | Rollback + restart |
| DATA | Data loss, corruption, accidental delete | Restore from backup |
| INTEGRATION | Provider failure, rate limit exceeded | Circuit break + failover |

## Triage Flow

### 1. Detection
- Automated alert (health check, error rate threshold, Prometheus alert)
- User report (support ticket, user feedback, social mention)
- Manual observation (operator dashboard, log review)

### 2. Classification
- Determine severity (SEV1–SEV4)
- Assign incident class (SECURITY, TRADING, PLATFORM, DATA, INTEGRATION)
- Open incident ticket/tracker entry with timestamp

### 3. Initial Assessment
- Check `/health` endpoint for backend status
- Review recent logs (`make server-logs` or `journalctl`)
- Check error rate on `/api/metrics`
- Verify database connectivity
- Assess blast radius and user impact

## Communication Flow

### SEV1/SEV2
1. Notify on-call engineer immediately
2. Post incident notification to designated channel
3. Provide status updates every 30 minutes (SEV1) or every 60 minutes (SEV2)
4. Declare resolution when service is restored or workaround is in place

### SEV3/SEV4
1. Log issue in tracking system
2. Assign to appropriate team member
3. Update when fix is deployed

## Safety Lock Activation

If the incident involves:
- **Security breach**: Activate emergency halt immediately
- **Unexpected trading behavior**: Activate kill switch + halt
- **Data integrity issue**: Stop all write operations

```bash
# Emergency halt (API available)
curl -X POST http://localhost:8005/api/risk/emergency-halt \
  -H 'Authorization: Bearer <admin-token>' \
  -H 'Content-Type: application/json' \
  -d '{"reason":"<incident-description>"}'

# Kill switch (if API unavailable)
docker compose -f docker-compose.prod.yml stop
```

## Rollback Decision

Criteria for rollback:
- SEV1/SEV2 incident introduced by recent deployment
- Cannot be resolved with hotfix within SLO timeframes
- Safety controls were bypassed or are malfunctioning

Procedure:
1. Confirm rollback target (previous stable version)
2. Execute rollback per `docs/runbooks/ROLLBACK_RUNBOOK.md`
3. Verify service health after rollback
4. Post-incident: determine root cause before re-deploying

## Evidence Collection

For all SEV1 and SEV2 incidents:

1. **Logs**: Capture backend logs, frontend logs, and database logs
2. **Metrics**: Export Prometheus metrics snapshot
3. **State**: Record service state (running services, database size, connections)
4. **Timeline**: Create chronological timeline of events
5. **Actions**: Document all actions taken during response

```bash
# Collect logs for evidence
docker logs backend --tail 1000 > incident-logs/backend-$(date +%Y%m%d-%H%M%S).log
docker logs frontend --tail 1000 > incident-logs/frontend-$(date +%Y%m%d-%H%M%S).log

# Collect support bundle (no secrets)
SUPPORT_BUNDLE_INCLUDE_SECRETS=false make support-bundle
```

## Postmortem

After every SEV1 and SEV2 incident:

1. **Root cause analysis**: Determine the underlying cause
2. **Impact assessment**: Quantify user impact and duration
3. **Action items**: Define preventive measures
4. **Timeline**: Finalize the incident timeline
5. **Review**: Schedule postmortem review within 5 business days

Postmortem document template:
```markdown
# Postmortem: [INCIDENT TITLE]
- Date: YYYY-MM-DD
- Severity: SEV1/SEV2
- Duration: HH:MM
- Impact: [description]

## Timeline
- HH:MM — Detection
- HH:MM — Classification
- HH:MM — Mitigation started
- HH:MM — Resolution

## Root Cause
[description]

## Action Items
- [ ] Action 1 (owner, due date)
- [ ] Action 2 (owner, due date)

## Lessons Learned
[description]
```

## No-Secret Logging Policy

- Never log passwords, tokens, API keys, JWT secrets, or database credentials
- Never log full request/response bodies for sensitive endpoints
- Audit logs exclude sensitive field values
- Support bundle generation excludes secrets by default (`SUPPORT_BUNDLE_INCLUDE_SECRETS=false`)
- Any log containing a potential secret must be rotated and sanitized immediately
- All incident evidence must be scanned for secrets before storage or sharing

## Related Documents

- Rollback procedure: `docs/runbooks/ROLLBACK_RUNBOOK.md`
- Kill switch: `docs/runbooks/KILL_SWITCH.md`
- Backup/restore: `docs/runbooks/BACKUP_RESTORE_RUNBOOK.md`
- Risk halt: `docs/runbooks/RISK_HALT_RUNBOOK.md`
- SLO definitions: `docs/ops/SLO_DEFINITIONS.md`
