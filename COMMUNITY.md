# zDash Community

zDash is a safety-first AI operations dashboard and agent runtime for staged automation, trading simulation, governance, observability, and enterprise control workflows.

Public/support domain:

```text
https://zdash.zeaz.dev
```

Cloudflare operator source of truth:

```text
https://github.com/CVSz/zeaz-platform
```

## Community Goals

The zDash community exists to build and review automation systems that are:

- safe by default
- testable
- auditable
- dry-run first
- mock-friendly
- tenant-aware where applicable
- respectful of security and privacy

## Where to Start

Read these files first:

- `README.md` for the project overview
- `AGENTS.md` for agent/contributor operating rules
- `CONTRIBUTING.md` for contribution workflow
- `SECURITY.md` for vulnerability handling
- `CODEOFCONDUCT.md` for behavior expectations
- `docs/prompt/phaseXX.prompt` for phase-specific work

## Communication Guidelines

When opening issues or discussions:

- describe the expected behavior
- include reproduction steps when possible
- include logs only after removing private data
- mention the affected phase, module, or workflow
- include validation commands already run
- avoid posting credentials, tokens, cookies, private keys, or customer data

## Support Domain

`zdash.zeaz.dev` is the supported public domain for zDash. Cloudflare routing and edge operations for this domain are managed in `CVSz/zeaz-platform`.

Use `cvsz/zdash` for application-level issues, including:

- backend bugs
- frontend bugs
- dashboard UX
- tests
- local Docker behavior
- phase prompt implementation
- docs in this app repository

Use `CVSz/zeaz-platform` for Cloudflare/operator work, including:

- DNS
- Pages or Tunnel routing
- Cloudflare Access
- WAF and API Shield
- edge health checks
- support-domain deployment automation

## Safety Culture

Do not ask maintainers or contributors to bypass safety gates. zDash must preserve dry-run, mock, read-only, or approval-gated defaults for external or customer-impacting actions.

## Good First Contributions

Good first tasks include:

- documentation cleanup
- typo fixes
- tests for existing modules
- mock adapter improvements
- frontend type alignment
- safer error messages
- runbook updates
- issue reproduction scripts that do not require real provider credentials

## Maintainer Notes

Maintainers should keep the community docs aligned with:

- `AGENTS.md`
- `SECURITY.md`
- `.codex/cloud/README.md`
- `docs/prompt/`
- the Cloudflare operator boundary in `CVSz/zeaz-platform`
