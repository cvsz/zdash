#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# =============================================================================
# zDash GitHub Environment Sync From .env Files
# =============================================================================
#
# Reads local env files and syncs keys into a GitHub Actions Environment.
# - Secret-looking keys become GitHub Environment Secrets.
# - Non-secret keys become GitHub Environment Variables.
# - Supports dry-run and explicit stale cleanup.
# - Never prints secret values.
#
# Default env overlay order, if files exist:
#   .env
#   .env.local
#   .env.production
#   .env.cloudflare
#   frontend/.env
#   frontend/.env.local
#   frontend/.env.production
#
# Usage:
#   bash scripts/github/bootstrap-env-from-env.sh --repo cvsz/zdash --env dev --dry-run
#   bash scripts/github/bootstrap-env-from-env.sh --repo cvsz/zdash --env dev --yes
#   bash scripts/github/bootstrap-env-from-env.sh --repo cvsz/zdash --env dev --delete-stale --yes
#
# =============================================================================

REPO="cvsz/zdash"
GH_ENV="dev"
DRY_RUN=false
YES=false
DELETE_STALE=false
INCLUDE_EMPTY=false
DECLARE_ONLY=false
FILES=()
FORCE_SECRET_KEYS=()
FORCE_VARIABLE_KEYS=(
  CLOUDFLARE_ACCOUNT_ID
  CLOUDFLARE_ZONE_ID
)
MANAGED_PREFIXES="APP_,BACKEND_,FRONTEND_,CORS_,DATABASE_,DB_,PRODUCTION_,AUTH_,METRICS_,JWT_,BOOTSTRAP_,DEFAULT_,TRADING_,DRY_,LIVE_,MT5_,RISK_,MAX_,EMERGENCY_,SOFT_,ALLOW_,REQUIRE_,HARD_,SCHEDULER_,FRIDAY_,IOT_,TAPO_,NSSM_,BACKTEST_,PRIMARY_,MIN_,OPTIMIZER_,CONTENT_,EDITOR_,GRAPHIC_,SOCIAL_,MULTI_,TENANT_,WORKSPACE_,WORKER_,REALTIME_,NOTIFICATION_,ALERT_,EMAIL_,SMTP_,WEBHOOK_,CLOUDFLARE_,K8S_,RELEASE_,AIOPS_,GOVERNANCE_,COMPLIANCE_,DESKTOP_,PUBLIC_,WAITLIST_,INVITE_,TELEMETRY_,SOVEREIGN_,DEFAULT_DATA_,ALLOWED_,DISALLOWED_,DATA_,CROSS_,CUSTOMER_,KMS_,EDGE_,ONPREM_,GLOBAL_,DIGITAL_,IMPACT_,BLAST_,TWIN_"
SECRET_KEY_REGEX='(TOKEN|SECRET|PASSWORD|PASS|PRIVATE_KEY|API_KEY|ACCESS_KEY|CLIENT_SECRET|WEBHOOK_SECRET|DATABASE_URL|REDIS_URL|BROKER_URL|DSN|SOPS_AGE_KEY|TUNNEL_SECRET)$|(^|_)KEY$'

usage(){
  cat <<'USAGE'
Usage:
  scripts/github/bootstrap-env-from-env.sh [options]

Options:
  --repo <owner/name>          GitHub repository. Default: cvsz/zdash
  --env <name>                 GitHub Environment name. Default: dev
  --file <path>                Env file to read. Repeatable. If omitted, common .env files are auto-discovered.
  --dry-run                    Print planned actions without creating/updating/deleting anything.
  --yes                        Required for live sync and stale cleanup.
  --delete-stale               Delete managed GitHub env vars/secrets not present in parsed env files.
  --include-empty              Upload empty values too. Default skips empty values.
  --secret-key <KEY>           Force KEY to be uploaded as secret. Repeatable.
  --variable-key <KEY>         Force KEY to be uploaded as variable. Repeatable.
  --managed-prefixes <csv>     Prefix allow-list for --delete-stale cleanup.
  --declare-only               Create GitHub Environment only; do not upload variables/secrets.
  --help                       Show this help.

Safe defaults:
  - Secret values are never printed.
  - Empty values are skipped by default.
  - Stale deletion requires --delete-stale --yes.
  - .env.example is never auto-loaded.
USAGE
}

log(){ printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }
warn(){ log "WARN: $*" >&2; }
die(){ log "ERROR: $*" >&2; exit 1; }
has(){ command -v "$1" >/dev/null 2>&1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --env) GH_ENV="${2:-}"; shift 2 ;;
    --file) FILES+=("${2:-}"); shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --yes) YES=true; shift ;;
    --delete-stale) DELETE_STALE=true; shift ;;
    --include-empty) INCLUDE_EMPTY=true; shift ;;
    --secret-key) FORCE_SECRET_KEYS+=("${2:-}"); shift 2 ;;
    --variable-key) FORCE_VARIABLE_KEYS+=("${2:-}"); shift 2 ;;
    --managed-prefixes) MANAGED_PREFIXES="${2:-}"; shift 2 ;;
    --declare-only) DECLARE_ONLY=true; shift ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[[ -n "$REPO" ]] || die "--repo is required"
[[ -n "$GH_ENV" ]] || die "--env is required"
has gh || die "gh CLI is required"
has jq || die "jq is required"
has python3 || die "python3 is required"
has base64 || die "base64 is required"

if [[ "$DRY_RUN" != "true" && "$YES" != "true" ]]; then
  die "live sync requires --yes. Use --dry-run first."
fi

if [[ "$DELETE_STALE" == "true" && "$YES" != "true" && "$DRY_RUN" != "true" ]]; then
  die "--delete-stale requires --yes or --dry-run"
fi

if [[ "${#FILES[@]}" -eq 0 ]]; then
  for candidate in .env .env.local .env.production .env.cloudflare frontend/.env frontend/.env.local frontend/.env.production; do
    [[ -f "$candidate" ]] && FILES+=("$candidate")
  done
fi

[[ "${#FILES[@]}" -gt 0 ]] || die "no env files found. Pass --file .env or create a local .env."

for file in "${FILES[@]}"; do
  [[ -f "$file" ]] || die "env file missing: $file"
  case "$file" in
    *.example|*.sample) die "refusing to sync example/template file: $file" ;;
  esac
done

if [[ "$DRY_RUN" != "true" ]]; then
  gh auth status >/dev/null 2>&1 || die "gh auth login is required"
fi

key_in_list(){
  local key="$1" item
  shift
  for item in "$@"; do
    [[ "$item" == "$key" ]] && return 0
  done
  return 1
}

is_secret_key(){
  local key="$1"
  key_in_list "$key" "${FORCE_VARIABLE_KEYS[@]}" && return 1
  key_in_list "$key" "${FORCE_SECRET_KEYS[@]}" && return 0
  [[ "$key" =~ $SECRET_KEY_REGEX ]]
}

is_managed_key(){
  local key="$1" prefix
  IFS=',' read -r -a prefixes <<< "$MANAGED_PREFIXES"
  for prefix in "${prefixes[@]}"; do
    prefix="${prefix//[[:space:]]/}"
    [[ -z "$prefix" ]] && continue
    [[ "$key" == "$prefix"* ]] && return 0
  done
  return 1
}

parse_rows(){
  python3 - "$INCLUDE_EMPTY" "${FILES[@]}" <<'PY'
from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

include_empty = sys.argv[1].lower() == "true"
files = [Path(p) for p in sys.argv[2:]]
assign = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
values: dict[str, tuple[str, str]] = {}


def normalize(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value

for path in files:
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = assign.match(line)
        if not match:
            print(f"WARN: {path}:{lineno}: ignored non-assignment line", file=sys.stderr)
            continue
        key, value = match.group(1), normalize(match.group(2))
        if value == "" and not include_empty:
            continue
        values[key] = (value, str(path))

for key in sorted(values):
    value, source = values[key]
    encoded = base64.b64encode(value.encode("utf-8")).decode("ascii")
    print(f"{key}\t{encoded}\t{source}")
PY
}

rows_file="$(mktemp)"
desired_file="$(mktemp)"
desired_secrets_file="$(mktemp)"
desired_vars_file="$(mktemp)"
trap 'rm -f "$rows_file" "$desired_file" "$desired_secrets_file" "$desired_vars_file"' EXIT
parse_rows > "$rows_file"

if [[ ! -s "$rows_file" ]]; then
  warn "no non-empty env values found after parsing: ${FILES[*]}"
fi

while IFS=$'\t' read -r key encoded source; do
  [[ -n "$key" ]] || continue
  printf '%s\n' "$key" >> "$desired_file"
  if is_secret_key "$key"; then
    printf '%s\n' "$key" >> "$desired_secrets_file"
  else
    printf '%s\n' "$key" >> "$desired_vars_file"
  fi
done < "$rows_file"

sort -u -o "$desired_file" "$desired_file"
sort -u -o "$desired_secrets_file" "$desired_secrets_file"
sort -u -o "$desired_vars_file" "$desired_vars_file"

log "Repo: $REPO"
log "GitHub Environment: $GH_ENV"
log "Input files: ${FILES[*]}"
log "Parsed keys: $(wc -l < "$desired_file" | tr -d ' ')"
log "Variables: $(wc -l < "$desired_vars_file" | tr -d ' ')"
log "Secrets: $(wc -l < "$desired_secrets_file" | tr -d ' ')"

if [[ "$DRY_RUN" == "true" ]]; then
  log "DRY-RUN: would create/update GitHub environment: $GH_ENV"
else
  log "Creating/updating GitHub environment: $GH_ENV"
  gh api --method PUT -H "Accept: application/vnd.github+json" "/repos/${REPO}/environments/${GH_ENV}" >/dev/null
fi

if [[ "$DECLARE_ONLY" == "true" ]]; then
  log "declare-only requested; environment sync complete"
  exit 0
fi

while IFS=$'\t' read -r key encoded source; do
  [[ -n "$key" ]] || continue
  value="$(printf '%s' "$encoded" | base64 --decode)"
  if is_secret_key "$key"; then
    if [[ "$DRY_RUN" == "true" ]]; then
      printf 'DRY-RUN secret   %-42s source=%s len=%s\n' "$key" "$source" "${#value}"
    else
      gh secret set "$key" --env "$GH_ENV" --repo "$REPO" --body "$value" >/dev/null
      printf 'SET     secret   %-42s source=%s len=%s\n' "$key" "$source" "${#value}"
    fi
  else
    if [[ "$DRY_RUN" == "true" ]]; then
      printf 'DRY-RUN variable %-42s source=%s len=%s\n' "$key" "$source" "${#value}"
    else
      gh variable set "$key" --env "$GH_ENV" --repo "$REPO" --body "$value" >/dev/null
      printf 'SET     variable %-42s source=%s len=%s\n' "$key" "$source" "${#value}"
    fi
  fi
done < "$rows_file"

delete_stale_key(){
  local kind="$1" key="$2"
  if [[ "$DRY_RUN" == "true" ]]; then
    printf 'DRY-RUN delete %-8s %s\n' "$kind" "$key"
    return 0
  fi
  case "$kind" in
    variable) gh api --method DELETE "/repos/${REPO}/environments/${GH_ENV}/variables/${key}" >/dev/null ;;
    secret) gh api --method DELETE "/repos/${REPO}/environments/${GH_ENV}/secrets/${key}" >/dev/null ;;
    *) die "unknown stale delete kind: $kind" ;;
  esac
  printf 'DELETE  %-8s %s\n' "$kind" "$key"
}

if [[ "$DELETE_STALE" == "true" ]]; then
  log "Stale cleanup enabled for managed prefixes: $MANAGED_PREFIXES"
  if [[ "$YES" != "true" && "$DRY_RUN" != "true" ]]; then
    die "stale cleanup requires --yes or --dry-run"
  fi

  existing_vars="$(gh api "/repos/${REPO}/environments/${GH_ENV}/variables" --paginate --jq '.variables[].name' 2>/dev/null || true)"
  existing_secrets="$(gh api "/repos/${REPO}/environments/${GH_ENV}/secrets" --paginate --jq '.secrets[].name' 2>/dev/null || true)"

  while IFS= read -r key; do
    [[ -n "$key" ]] || continue
    if grep -Fxq "$key" "$desired_secrets_file" || ! grep -Fxq "$key" "$desired_file" && is_managed_key "$key"; then
      delete_stale_key variable "$key"
    fi
  done <<< "$existing_vars"

  while IFS= read -r key; do
    [[ -n "$key" ]] || continue
    if grep -Fxq "$key" "$desired_vars_file" || ! grep -Fxq "$key" "$desired_file" && is_managed_key "$key"; then
      delete_stale_key secret "$key"
    fi
  done <<< "$existing_secrets"
fi

log "GitHub environment sync completed"
