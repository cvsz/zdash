# zDash vX.Y.Z Release Notes

## Status

READY / HOLD

## Release summary

Brief description of what this release includes.

## New features

- Feature 1
- Feature 2
- Feature 3

## Bug fixes

- Fix 1
- Fix 2

## Safety changes

- [ ] No safety defaults removed
- [ ] All external actions default to dry-run/read-only/mock
- [ ] High-risk actions remain approval-gated
- [ ] Production safety checks pass

## Validation

| Check | Result |
|-------|--------|
| Backend tests | PASS / FAIL |
| Frontend tests | PASS / FAIL |
| Frontend build | PASS / FAIL |
| Safety scan | PASS / FAIL |
| Docker compose config | PASS / FAIL |
| Secret scan | PASS / FAIL |

## Breaking changes

- None
- (list any)

## Upgrade notes

- `make prod-env-generate` to refresh `.env.production`
- `make release-tag RELEASE_TAG=vX.Y.Z` to tag

## Rollback

See `docs/runbooks/rollback-runbook.md`.

## Release artifacts

- Docker images: `zdash-backend:VERSION`, `zdash-frontend:VERSION`
- Release tag: `vX.Y.Z`
