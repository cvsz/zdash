# Security Policy

## Supported Project

zDash is an AI operations dashboard and agent-runtime blueprint for staged backend, frontend, automation, governance, and safety-gated operations.

Production/support domain:

```text
https://zdash.zeaz.dev
```

The public support domain is operated through the Cloudflare operator system maintained in:

```text
https://github.com/CVSz/zeaz-platform
```

Cloudflare route, Pages, Tunnel, DNS, Access, WAF, and related edge automation changes should be made in the operator repository, not directly in this application repository.

## Reporting a Vulnerability

Do not open public issues for exploitable vulnerabilities, credentials, tokens, private customer data, or bypass instructions.

Preferred private reporting path:

1. Open a private security advisory when GitHub security advisories are enabled for this repository.
2. If advisories are unavailable, contact the repository owner/maintainer through the trusted private channel already used for this project.
3. Include a minimal reproduction, affected paths, impact, and suggested mitigation.

Do not include real secrets in reports. Redact tokens, API keys, private keys, cookies, and customer data.

## Scope

In scope:

- Authentication and authorization bypasses
- Tenant/workspace isolation flaws
- Secret exposure in code, logs, bundles, artifacts, prompts, or frontend builds
- Unsafe defaults for trading, IoT, social posting, update, rollback, support, or remote relay flows
- Cloudflare route/support-domain misconfiguration affecting `zdash.zeaz.dev`
- CI/CD, Docker, deployment, and dependency security issues
- XSS, SSRF, command injection, path traversal, deserialization, or unsafe plugin execution

Out of scope unless they demonstrate direct exploitability:

- Missing cosmetic headers in local-only development mode
- Dependency scanner noise without a reachable path
- Rate-limit findings against mock or dry-run endpoints only
- Reports requiring real production credentials not available to reporters

## Safety-Critical Defaults

The following must remain disabled, dry-run, mock, read-only, or approval-gated by default:

- Live trading
- Real broker order execution
- Real IoT power actions
- Real social posting
- Secret export
- Raw shell relay
- Real infrastructure mutation
- Real update apply or rollback execution
- Unreviewed plugin execution
- Plugin secret access
- Destructive automation

Do not bypass:

- Guardian risk checks
- Drawdown guard checks
- Kill switch / halt flag checks
- Content approval checks
- RBAC
- Tenant isolation
- Audit logging
- Policy, certification, and attestation gates where present
- Backup/readiness checks before mutation

## Cloudflare Operator Boundary

`zdash.zeaz.dev` is the supported public domain for zDash. Cloudflare operational source of truth lives in `CVSz/zeaz-platform`.

Application repository responsibilities:

- app code
- local config defaults
- backend/frontend builds
- tests
- documentation

Cloudflare operator repository responsibilities:

- DNS
- Pages/Tunnel routing
- Access/WAF/API Shield policies
- edge health checks
- token rotation automation
- production support domain rollout

## Handling Secrets

Never commit:

- `.env`
- real API keys
- provider tokens
- private keys
- SSH keys
- broker credentials
- Stripe secrets
- Cloudflare tokens
- webhook secrets
- customer data

Allowed:

- `.env.example`
- empty placeholder values
- `env.safe.example`
- clearly fake examples that do not match scanner patterns

## Disclosure and Fix Process

Maintainers should:

1. Acknowledge the report when received.
2. Reproduce and classify severity.
3. Patch root cause.
4. Add regression tests where practical.
5. Update documentation and safety gates when relevant.
6. Coordinate disclosure once the fix is available.

Security fixes should prefer small, reviewable changes and must not weaken existing tests or safety defaults.
