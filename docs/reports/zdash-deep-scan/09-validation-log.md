# zDash Validation Log

| Date | Commit | Command | Result | Notes |
|---|---|---|---|---|
| 2026-08-23 | f34c874 | `pip-audit -r backend/requirements.lock` | PASS | 0 known vulnerabilities (now blocking in release-validate) |
| 2026-08-23 | f34c874 | `npm audit --audit-level=high` (frontend) | PASS | 0 vulnerabilities |
| 2026-08-23 | f34c874 | backend: ruff format --check / ruff check | PASS | 497 files |
| 2026-08-23 | f34c874 | `mypy .` (backend, strict scope) | PASS | 0 errors in 497 files after mypy-debt cleanup |
| 2026-08-23 | f34c874 | `bandit -r backend/app -q -lll` | PASS | CI security gate |
| 2026-08-23 | f34c874 | pytest (backend, Python 3.14.4) | PASS | 732 tests, sqlite + PostgreSQL 18.6 targets |
| 2026-08-23 | f34c874 | alembic upgrade head / current | PASS | head = 20260805_0001 (sqlite, PG16, PG18) |
| 2026-08-23 | f34c874 | frontend: tsc build-config, eslint, vitest, vite build | PASS | 114/114 tests; testTimeout raised to 20s |
| 2026-08-23 | f34c874 | docker compose config (+ prod, prod+secrets overlay) | PASS | placeholder env for prod validation |
| 2026-08-23 | f34c874 | docker compose up -d full stack | PASS | 5/5 containers healthy |
| 2026-08-23 | f34c874 | GitHub Actions on main | GREEN | ci, backend-ci, frontend-ci, lint, security-ci, codeql, e2e, pages-deploy |
| 2026-08-23 | d1f804f | v0.42.0-rc3 tag workflows | GREEN | ci, backend/frontend/docker-ci, release, release-check/-validate/-evidence |
