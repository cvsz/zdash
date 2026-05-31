---
name: Feature request
about: Suggest an idea for zDash
title: '[feature] '
labels: enhancement
assignees: ''

---

**Problem statement**
What problem does this solve? Ex. I'm frustrated when [...]

**Proposed solution**
What should happen and which area it affects:
- [ ] Backend (FastAPI / Python)
- [ ] Frontend (React / TypeScript)
- [ ] Infrastructure (Docker / CI/CD)
- [ ] Docs / runbooks / prompts

**Phase reference**
Which phase prompt in `docs/prompts/` does this extend? (e.g. phase08, phase14)

**Safety checklist (required)**
- [ ] Defaults to dry-run / read-only / mock / approval-gated
- [ ] Never enables live trading, real broker/IoT/social actions, secret export, or infrastructure mutation by default
- [ ] Never bypasses Guardian, RBAC, audit logging, tenant isolation, kill-switch, or approval gates
- [ ] Real mutations require: admin permission + typed confirmation + validation preflight + audit event + rollback plan

**Alternatives considered**

**Additional context**
