# Git Safe Push Workflow

## Quick Reference

```bash
make git-safe-status                 # Check status + risky file detection
make git-safe-add                    # Stage all safe files (auto-cleans artifacts)
make git-safe-add ARGS="file1 file2" # Stage specific files (rejects unsafe paths)
make git-safe-commit MESSAGE="..."   # Commit with pre-commit safety scan
make git-safe-push                   # Validate, status, push
```

## Step by Step

### 1. Check status

```bash
make git-safe-status
```

Shows short status, working tree diff, staged diff, and highlights risky files (`.env`, `*.pem`, `Makefile.bak.*`, etc.).

### 2. Stage files

```bash
make git-safe-add
```

Runs `clean-local-artifacts.sh` first, then stages all safe project files. Never stages: `.env`, `.env.*`, `frontend/.env.local`, `Makefile.bak.*`, `*.bak`, `backend.log`, `frontend.log`, `.runtime/`, `node_modules/`, `backend/.venv/`.

For specific files:

```bash
make git-safe-add ARGS="Makefile backend/app/risk/high_risk_policy.py"
```

### 3. Commit

```bash
make git-safe-commit MESSAGE="Fix validation scan"
```

Before committing, runs:
- `safe-status.sh` — show staged files
- `make safety-scan` — forbidden files, port 8000 scan, secret scan
- Secret pattern scan on staged diff — AWS keys, OpenAI tokens, GitHub tokens, Claude/Anthropic keys, Cloudflare tokens, private keys

Test fixture strings that match secret patterns are allowed (no false-positive blocking).

### 4. Push

```bash
make git-safe-push
```

Runs `make validate-fast` + `safe-status.sh`, then pushes to `origin/main`.

## GitHub Push Protection Recovery

If GitHub push protection blocks your push:

```bash
# 1. Do NOT use the "unblock" URL for real secrets
# 2. Rotate/delete any leaked cloud keys immediately at the provider

# 3. Recover local branch
git fetch origin main
git reset --soft origin/main

# 4. Remove secrets from files
# 5. Re-commit safely
bash scripts/git/safe-add.sh
make validate-fast
bash scripts/git/safe-commit.sh "Remove leaked secret"
bash scripts/git/safe-push.sh
```

## Secret Rotation

If a real secret was exposed:

1. **Revoke the compromised key** at the provider immediately (AWS IAM, GitHub settings, OpenAI dashboard, Cloudflare dashboard, etc.)
2. **Generate a new key**
3. **Update `.env.production`** on the server
4. **Rotate any dependent services** that used the old key
5. **Verify no unauthorized access** in provider audit logs

## Why Not Use Unblock URL

GitHub's "unblock" URL bypasses push protection. For real secrets (not test fixtures), this defeats the safety mechanism. Always rotate the key instead.
