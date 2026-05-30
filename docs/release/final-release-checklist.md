# Final Release Checklist

## Pre-release gates

- [ ] `make safety-scan` passes
- [ ] `make validate-fast` passes
- [ ] `make validate` passes
- [ ] Frontend production build passes (`make frontend-build`)
- [ ] Backend tests pass (`make backend-test`)
- [ ] Secret scan passes (no secrets in source)
- [ ] Docker compose config validates (`docker compose -f docker-compose.prod.yml config`)
- [ ] `.env.example` is complete and accurate
- [ ] `.env.production.example` is complete and accurate
- [ ] All docs updated
- [ ] Rollback runbook exists (`docs/runbooks/rollback-runbook.md`)
- [ ] Incident response runbook exists (`docs/runbooks/incident-response-runbook.md`)
- [ ] Final release runbook exists (`docs/runbooks/final-release-runbook.md`)
- [ ] Production fail-closed policy exists (`docs/security/production-fail-closed-policy.md`)
- [ ] Production config fail-closed tests pass
- [ ] Provider contract tests present (skeletons or full)
- [ ] Phase traceability matrix complete (`docs/reports/phase-traceability-matrix.md`)
- [ ] Final release readiness report generated (`docs/reports/final-release-readiness-report.md`)

## Release day

- [ ] Tag release (`make release-tag RELEASE_TAG=vX.Y.Z`)
- [ ] Build Docker images (`make docker-build`)
- [ ] Validate compose config with new images
- [ ] Deploy to staging
- [ ] Run validation on staging
- [ ] Deploy to production
- [ ] Verify health (`curl http://localhost:8005/health`)
- [ ] Verify safety check (`curl http://localhost:8005/api/admin/safety-check`)
- [ ] Verify frontend loads

## Post-release

- [ ] Monitor logs for first 24 hours
- [ ] Check alert rules fire correctly
- [ ] Confirm dry-run mode active
- [ ] Update release notes
- [ ] Push release tag and notes to GitHub
