---
name: Bug report
about: Report a bug to help improve zDash
title: '[bug] '
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of the bug.

**Area**
- [ ] Backend (FastAPI / Python / Pydantic / SQLModel)
- [ ] Frontend (React / TypeScript / Tailwind / Vitest)
- [ ] Infrastructure (Docker / compose / CI/CD)
- [ ] Safety / risk system (Guardian, kill-switch, high-risk policy, fail-closed)
- [ ] Docs / runbooks / prompts
- [ ] Release / versioning
- [ ] Other:

**To Reproduce**
Steps to reproduce with exact commands:

```bash
# example
make backend-test
```

1.
2.
3.

**Expected behavior**

**Actual behavior** (logs, errors, screenshots)

**Safety impact**
Does this affect any safety invariant? (see AGENTS.md §4)
- [ ] No safety impact
- [ ] Potential safety bypass — explain:

**Environment**
- zDash version: `{{ "$(cat VERSION || git describe --tags)" }}`
- `APP_ENV`: `development` / `production`
- `DRY_RUN`: `true` / `false`
- Backend port: `8005` / other:
- Browser (if frontend):

**Validation before filing**
- [ ] `make safety-scan` passes
- [ ] `make validate-fast` passes (or relevant subset)
- [ ] `make backend-test` and/or `make frontend-test` pass individually
- [ ] Verified against latest `main`

**Additional context**
