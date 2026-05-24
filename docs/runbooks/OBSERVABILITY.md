# OBSERVABILITY

## Purpose
Operate metrics and dashboards.

## Prerequisites
- Observability profile enabled

## Commands
```bash
docker compose --profile observability up -d
curl http://localhost:8000/metrics
```

## Expected output
- Prometheus and Grafana running.
- Metrics endpoint exposing counters/histograms.

## Failure handling
- Validate scrape config in `deploy/prometheus/prometheus.yml`.

## Rollback steps
- Disable observability profile and keep core production profile.

## Safety notes
- Metrics endpoint must not expose secrets.
