# Code of Conduct

## Our Pledge

We as contributors, maintainers, and community participants pledge to make participation in zDash welcoming, respectful, and productive.

zDash is a safety-first AI operations dashboard and agent runtime. Contributions may touch automation, trading simulation, governance, observability, security operations, and Cloudflare-backed support-domain workflows. The project expects careful, respectful collaboration because mistakes in automation and infrastructure can create real operational risk.

## Expected Behavior

Examples of behavior that contributes to a positive environment:

- using welcoming and inclusive language
- respecting different experience levels and viewpoints
- giving constructive technical feedback
- accepting responsibility and correcting mistakes
- keeping discussions focused on the project and user safety
- documenting assumptions and limitations
- preserving safety gates and secure defaults
- reporting security issues through private channels when appropriate

## Unacceptable Behavior

Examples of unacceptable behavior include:

- harassment, insults, intimidation, or personal attacks
- discriminatory language or behavior
- publishing private information without permission
- posting credentials, tokens, private keys, or private customer data
- encouraging bypass of safety controls
- pressuring contributors to enable unsafe live actions by default
- knowingly submitting malicious code, hidden backdoors, or destructive automation
- abusing issue trackers, reviews, or discussions with spam or bad-faith behavior

## Safety and Security Expectations

Contributors must not request or submit changes that bypass:

- Guardian or risk checks
- kill switch / halt flag controls
- RBAC
- tenant isolation
- audit logging
- content approval checks
- policy, certification, or attestation gates when present
- backup/readiness checks before real mutation

External or customer-impacting actions must default to dry-run, read-only, mock, simulation, or approval-gated mode.

## Support Domain Boundary

The zDash support domain is:

```text
https://zdash.zeaz.dev
```

Cloudflare operator work for this domain belongs in:

```text
https://github.com/CVSz/zeaz-platform
```

Respect the boundary between application code in `cvsz/zdash` and Cloudflare edge/operator automation in `CVSz/zeaz-platform`.

## Enforcement

Maintainers may remove, edit, or reject comments, commits, issues, pull requests, and other contributions that do not follow this Code of Conduct.

Maintainers may temporarily or permanently restrict participation for behavior they determine to be inappropriate, unsafe, threatening, offensive, or harmful.

## Reporting

Report conduct concerns to project maintainers through the trusted private channel already used for this project.

For exploitable vulnerabilities or secret exposure, follow `SECURITY.md` instead of opening a public issue.

## Attribution

This Code of Conduct is adapted from common open-source community standards and customized for the zDash safety-first automation context.
