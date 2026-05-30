#!/usr/bin/env bash
set -Eeuo pipefail

REPO="${REPO:-$PWD}"
OUT="${OUT:-$REPO/docs/reports/zdash-deep-scan}"
mkdir -p "$OUT"

cd "$REPO"

log() { printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }

log "Writing summary"
{
  echo "# zDash Deep Scan Summary"
  echo
  date -u
  echo
  echo "## Git"
  git rev-parse --short HEAD || true
  git branch --show-current || true
  git status --short || true
} > "$OUT/00-summary.md"

log "File inventory"
git ls-files | sort > "$OUT/01-file-inventory.txt"

log "Source inventory"
git ls-files | grep -E '\.(py|ts|tsx|js|jsx|mjs|cjs|sh|bash|yml|yaml|json|toml|md|css|scss|html|Dockerfile)$|Dockerfile$' | sort > "$OUT/02-source-inventory.txt" || true

log "Functions/classes/components index"
{
  echo "# zDash Function/Class/Component Index"
  echo
  git ls-files | grep -E '\.(py|ts|tsx|js|jsx|mjs|cjs|sh|bash)$' | while read -r f; do
    echo "## $f"
    grep -nE '^[[:space:]]*(async[[:space:]]+)?def[[:space:]]+[A-Za-z_][A-Za-z0-9_]*|^[[:space:]]*class[[:space:]]+[A-Za-z_][A-Za-z0-9_]*|^[[:space:]]*(export[[:space:]]+)?(async[[:space:]]+)?function[[:space:]]+[A-Za-z_][A-Za-z0-9_]*|^[[:space:]]*(export[[:space:]]+)?const[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=[[:space:]]*(async[[:space:]]*)?\(|^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*\(\)[[:space:]]*\{' "$f" || true
    echo
  done
} > "$OUT/03-functions-classes-components.txt"

log "Routes and API index"
{
  echo "# zDash Routes/API Index"
  echo
  echo "## FastAPI decorators"
  git grep -nE '@(app|router)\.(get|post|put|patch|delete|websocket)\(' -- '*.py' || true
  echo
  echo "## API strings"
  git grep -nE '(/api/|http://localhost:8005|VITE_API_BASE_URL|fetch\(|axios)' -- '*.ts' '*.tsx' '*.js' '*.jsx' '*.py' || true
  echo
  echo "## Frontend routes/links"
  git grep -nE 'Route|path=|href=|to=' -- '*.tsx' '*.ts' '*.jsx' '*.js' || true
} > "$OUT/04-routes-api.txt"

log "Environment variables index"
{
  echo "# zDash Env Var Index"
  echo
  git grep -nE '(^|[^A-Z0-9_])([A-Z][A-Z0-9_]{2,})=' -- '*.example' '*.md' '*.sh' '*.py' '*.ts' '*.tsx' '*.yml' '*.yaml' '*.toml' '.env*' 2>/dev/null || true
} > "$OUT/05-env-vars.txt"

log "Package and Make scripts"
{
  echo "# zDash Package and Make Scripts"
  echo
  echo "## Makefile targets"
  if [ -f Makefile ]; then
    grep -nE '^[A-Za-z0-9_.-]+:' Makefile || true
  fi
  echo
  echo "## package.json scripts"
  find . -maxdepth 4 -name package.json -print | while read -r p; do
    echo "### $p"
    node -e "const p=require('$p'); console.log(JSON.stringify(p.scripts||{}, null, 2))" 2>/dev/null || grep -n '"scripts"' -A80 "$p" || true
  done
} > "$OUT/06-package-make-scripts.txt"

log "Security patterns redacted"
{
  echo "# zDash Security Pattern Scan"
  echo
  echo "Secret-like values are redacted. Review file paths and variable names only."
  echo
  patterns='OPENAI_API_KEY|CLOUDFLARE_API_TOKEN|GITHUB_TOKEN|JWT_SECRET|PRIVATE KEY|DATABASE_URL|PASSWORD|SECRET|TOKEN|API_KEY'
  git grep -nE "$patterns" -- ':!*.png' ':!*.jpg' ':!*.jpeg' ':!*.webp' ':!*.gif' ':!*.lock' 2>/dev/null \
    | sed -E 's/(=|:).*/=<REDACTED>/' \
    | head -1000 || true
} > "$OUT/07-security-patterns-redacted.txt"

log "Docker and CI inventory"
{
  echo "# Docker and CI Inventory"
  echo
  echo "## GitHub Actions"
  find .github/workflows -type f -maxdepth 2 -print 2>/dev/null || true
  echo
  echo "## Docker"
  git ls-files | grep -E 'Dockerfile|docker-compose|compose\.ya?ml|infra/docker' || true
} > "$OUT/08-docker-ci-inventory.txt"

cat > "$OUT/09-validation-log.md" <<'MD'
# zDash Validation Log

| Date | Commit | Command | Result | Notes |
|---|---|---|---|
| TODO | TODO | make safety-scan | TODO | TODO |
| TODO | TODO | make validate-fast | TODO | TODO |
| TODO | TODO | make validate | TODO | TODO |
| TODO | TODO | docker compose config | TODO | TODO |
MD

cat > "$OUT/10-remediation-plan.md" <<'MD'
# zDash Remediation Plan

## P0

- Run and capture full validation.
- Add production fail-closed validator tests.
- Add high-risk action policy gate tests.
- Add secret scan over tracked files and release artifacts.

## P1

- Add phase traceability matrix.
- Add provider adapter contract tests.
- Add frontend safety-state tests.
- Add backend audit-event tests.

## P2

- Add SBOM.
- Add SLO/runbooks.
- Add incident response docs.
- Add backup/restore proof.
MD

log "Done: $OUT"
ls -la "$OUT"
