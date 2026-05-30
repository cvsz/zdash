#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# Accept message from env or first arg
MESSAGE="${MESSAGE:-}"
if [[ -z "$MESSAGE" && $# -ge 1 ]]; then
  MESSAGE="$*"
fi

if [[ -z "$MESSAGE" ]]; then
  echo "Error: Commit message is required."
  echo "Usage: MESSAGE=\"Fix validation scan\" $0"
  echo "   or: $0 \"Fix validation scan\""
  exit 1
fi

# Step 1: Show status
bash "$ROOT_DIR/scripts/git/safe-status.sh"

echo ""
echo "--- Safety Scan ---"
make -C "$ROOT_DIR" safety-scan || {
  echo "Safety scan failed. Fix issues before committing."
  exit 1
}

# Step 2: Scan staged diff for secrets
echo ""
echo "--- Secret Pattern Scan ---"

SECRET_PATTERNS=(
  "AKIA[0-9A-Z]{16}"                                        # AWS access key
  "(?i)aws_secret_access_key.*["']?[A-Za-z0-9/+=]{40}"      # AWS secret key
  "sk-[a-zA-Z0-9]{20,}"                                      # OpenAI key
  "ghp_[a-zA-Z0-9]{36}"                                      # GitHub PAT
  "gho_[a-zA-Z0-9]{36}"                                      # GitHub OAuth
  "sk-ant-api[0-9a-zA-Z_-]{32,}"                             # Claude/Anthropic
  "cf_api_token.*["']?[A-Za-z0-9_-]{40}"                    # Cloudflare
  "-----BEGIN.*PRIVATE KEY-----"                             # Private key
)

STAGED_DIFF=$(git -C "$ROOT_DIR" diff --cached 2>/dev/null || true)
SECRET_FOUND=false

for pattern in "${SECRET_PATTERNS[@]}"; do
  if echo "$STAGED_DIFF" | grep -qE "$pattern"; then
    # Check if matches are in test fixtures (allow known test strings)
    MATCHES=$(echo "$STAGED_DIFF" | grep -E "$pattern" || true)
    while IFS= read -r match; do
      # Skip if the match is in a test fixture file
      if echo "$match" | grep -qE "test_.*\.(py|ts|tsx|js)"; then
        continue
      fi
      echo "  ⚠ Potential secret pattern found: $pattern"
      SECRET_FOUND=true
    done <<< "$MATCHES"
  fi
done

if $SECRET_FOUND; then
  echo ""
  echo "Potential secrets detected in staged diff."
  echo "Review and remove before committing."
  echo "If these are false positives in test fixtures, use:"
  echo "  git commit -m \"$MESSAGE\""
  echo "to bypass (after careful review)."
  exit 1
fi

echo "  No secrets detected."

# Step 3: Commit
echo ""
echo "--- Committing ---"
echo "Message: $MESSAGE"
echo ""
git -C "$ROOT_DIR" commit -m "$MESSAGE"
echo "Commit successful."
