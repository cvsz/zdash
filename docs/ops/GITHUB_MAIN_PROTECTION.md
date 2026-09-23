# GitHub `main` Protection — Operator Procedure

**Status: not applied automatically.** The connected GitHub workflow used
for code changes cannot mutate repository administration settings. A
repository administrator must run the explicit, reviewable script below.

## Step 1 — verify the expected checks

After merging the isolated DR job, confirm the PR and resulting `main`
checks have passed. The protection policy references always-on PR jobs:

- `backend-tests`, `frontend-tests`, `docker-build` and `postgres-dr`
- `backend-lint`, `frontend-lint`
- `security`, `dependency-review`, `e2e`
- `analyze-python`, `analyze-javascript-typescript`

Do not add path-filtered checks such as `test-frontend` or
`sbom-and-evidence` as universally required; otherwise documentation-only
PRs can remain pending indefinitely. Confirm the exact check names shown
in GitHub's Checks UI before applying protection.

## Step 2 — review and apply

```bash
gh auth status
gh repo view cvsz/zdash --json nameWithOwner
bash scripts/github/configure-main-protection.sh --dry-run
# Requires a repository administrator's explicit action:
bash scripts/github/configure-main-protection.sh --apply
gh api repos/cvsz/zdash/branches/main --jq .protected
gh api repos/cvsz/zdash/branches/main/protection \
  --jq '{strict: .required_status_checks.strict, enforced: .enforce_admins.enabled}'
```

The script rejects missing admin permission. It requires pull requests,
strict status checks, resolution of discussions and linear history, applies
restrictions to administrators, and blocks forced pushes and deletion.

**Solo-owner constraint:** The initial policy requires PRs but sets the
minimum approving review count to **zero** to avoid locking the sole
maintainer out. Before customer production, assign a second trusted
reviewer, then increase the minimum to one and require CODEOWNERS review
where appropriate. Log any break-glass exception and reconcile it.

## Step 3 — confirm operational governance

- Open a test PR from a feature branch; verify an unmet required check
  blocks merging, and rerun it only after correcting the root cause.
- Verify branch deletion and force-push are rejected.
- Ensure dependency PRs #77–#81 are rebased and retested individually;
  never force-merge stale or failing dependency updates.
- Capture screenshots or API response metadata showing the active policy.
  Never publish a GitHub token or `gh auth` credential output.

This policy proves repository governance only. It is not external HTTPS,
database disaster recovery, customer RBAC, or production deployment evidence.
