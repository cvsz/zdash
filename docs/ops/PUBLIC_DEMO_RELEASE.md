# Public Demo and Production Deployment Boundary

This repository ships **two distinct artifacts**. A GitHub Pages build is a client-facing,
read-only **simulation**. The production frontend is an authenticated API client.
Never deploy the public-demo artifact as an authenticated control plane.

## Public demo (GitHub Pages)

Run from a clean repository worktree with no private frontend `.env*` overrides:

```bash
cd frontend
npm ci
npm run lint
npm test
npm run build:demo
```

The build generates an ignored `frontend/.env.public-demo` from the tracked
non-secret `frontend/public-demo.env.example` template, and uses a separate Vite mode,
and emits assets rooted at `/zdash/`. The public artifact uses hash routing (`#/team`, `#/risk`) so deep links
refresh without requiring server-side SPA rewrites. The Vite asset base stays
`/zdash/` for GitHub Pages. The read-only API adapter returns only explicit fixtures; a view
without one receives `DEMO_FIXTURE_UNAVAILABLE` rather than making a network
request. Every API mutation fails with `DEMO_READ_ONLY`.
Realtime and collaboration WebSocket paths are disabled; no live backend,
session key, wallet key, or provider key is distributed. The UI shows a
persistent PUBLIC DEMO / SIMULATED DATA banner.

`pages-deploy.yml` tests PRs but deploys only after a change reaches
`main` or an operator starts `workflow_dispatch`. Configure the repository's
Settings > Pages > Source to **GitHub Actions**. Expected URL:
`https://cvsz.github.io/zdash/`. Configure HTTP caching and monitor build
failures before sending clients the link.

For an InfinityFree domain at its document root, build the same offline-only
artifact with `npm run build:demo-root` and upload only the files inside
`frontend/dist/` to that domain's `htdocs/`. Do not upload `.env*`, source,
node_modules, or backend scripts. This mode uses root-relative assets and
hash routing and does not need an `.htaccess` rewrite. Do not reuse leaked
FTP credentials; rotate and store them outside source control first.

**Limits:** Demo screens with no offline fixture will show their error/empty
state. All displayed results are illustrative. This is not evidence of live
trading, data pipelines, real providers, or a successful production rollout.

## Production build

`infra/docker/frontend.Dockerfile` enforces authenticated, non-demo builds:
`VITE_AUTH_ENABLED=true`, `VITE_ENABLE_MOCK_FALLBACK=false`,
`VITE_PUBLIC_DEMO=false` and `VITE_APP_ENV=production`.
The frontend also requires authentication for any Vite production build
unless explicitly compiled as a public demo. Keep the backend behind
same-origin reverse proxy or a configured HTTPS API origin and enforce auth,
RBAC, tenant isolation, audit and rate limits **on the backend**.

Generate fresh secrets locally and supply `.env.production` outside Git.
Before applying Compose changes, verify the environment and inspect output:

```bash
cp .env.example .env.production
# Edit .env.production using a secrets manager; never reuse sample values.
python3 scripts/verify_prod_env.py .env.production
docker compose --env-file .env.production -f docker-compose.prod.yml config --quiet
docker compose --env-file .env.production -f docker-compose.prod.yml up -d
```

The production deployment must remain private until verified:
1. Production frontend login is enforced and unknown users are denied.
2. Browser devtools show no mock fallback or credentials and no cross-origin
   cleartext requests.
3. API health/readiness, auth, tenant RBAC and idempotent mutation tests pass.
4. PostgreSQL backup **and isolated restore**, audit logs, metrics/alerting,
   rollback and operational on-call have timestamped evidence.
5. Cloudflare Access/WAF/TLS, DNS, ownership and externally observed endpoint
   tests are verified by the operator.
6. Maintain explicit locks on live trading, IoT mutations and publication
   until separate human approvals and evidence exist.

**Security:** Rotate any FTP, database or hosting credentials shared via files,
chat or other plaintext channels. Never place them in `VITE_*`, Git history,
GitHub Pages, CI logs or public issue/PR text.
