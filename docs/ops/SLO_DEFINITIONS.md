# SLO Definitions

This document defines Service Level Objectives (SLOs) for the zDash platform. These are **target thresholds** and are not yet automatically measured. Implementation of automated SLO monitoring is a future enhancement.

## Availability SLO

| Metric | Target | Measurement |
|--------|--------|-------------|
| Uptime | 99.9% | Health endpoint (`/health`) returns 200 OK |
| Window | Rolling 30 days | Prometheus `/api/metrics` endpoint |
| Exclusions | Planned maintenance windows | |

**Calculation:** `(total_time - downtime) / total_time * 100`

**99.9% allows:** ~43 minutes of downtime per month, ~8.7 hours per year.

## API Latency SLO

| Metric | Target | Measurement |
|--------|--------|-------------|
| p95 response time | < 500ms | All API endpoints under `/api/*` |
| p99 response time | < 1000ms | All API endpoints under `/api/*` |
| Window | Rolling 5 minutes | |

**Measurement:** Latency is measured server-side from request receipt to response dispatch. Network transit time is excluded.

## Error-Rate SLO

| Metric | Target | Measurement |
|--------|--------|-------------|
| 5xx responses | < 1% of total requests | All API endpoints under `/api/*` |
| Window | Rolling 5 minutes | |

**Calculation:** `(5xx_responses / total_responses) * 100`

**Exclusions:** Health check endpoints (`/health`) are excluded from error-rate calculation.

## WebSocket/Realtime SLO

| Metric | Target | Measurement |
|--------|--------|-------------|
| p95 message latency | < 200ms | End-to-end from server send to client receipt |
| Connection stability | < 0.1% drop rate per session | |

**Note:** Realtime WebSocket latency is dependent on network conditions between server and client. These targets assume local/colocated deployments.

## CI/Release Validation SLO

| Metric | Target | Measurement |
|--------|--------|-------------|
| Validation completion | < 15 minutes | Full `make validate-fast` pipeline (safety scan + backend tests + frontend tests + build) |
| Cadence | Per commit on main branch | GitHub Actions CI |

## Backup/Restore SLO

| Metric | Target | Measurement |
|--------|--------|-------------|
| Recovery Time Objective (RTO) | < 1 hour | Time from incident declaration to service restoration |
| Recovery Point Objective (RPO) | < 24 hours | Maximum acceptable data loss window |
| Backup cadence | Daily | Automated via cron or GitHub Actions scheduled workflow |

**Procedure:** See `docs/runbooks/BACKUP_RESTORE_RUNBOOK.md`

## Incident Response SLO

| Severity | Response Time | Resolution Target |
|----------|--------------|-------------------|
| SEV1 | Acknowledged within 15 minutes | < 4 hours |
| SEV2 | Acknowledged within 1 hour | < 8 hours |
| SEV3 | Acknowledged within 4 hours | < 24 hours |
| SEV4 | Acknowledged within 1 business day | Next release |

**Procedure:** See `docs/runbooks/INCIDENT_RESPONSE.md`

## Future Monitoring

Automated SLO monitoring will require:

1. Prometheus recording rules for availability and error rate
2. Grafana dashboards for latency percentiles
3. Alertmanager rules for SLO burn-rate alerts
4. Synthetic monitoring (e.g., Playwright checks) for availability
5. Periodic SLO review and adjustment
