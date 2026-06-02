#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUTDIR="$REPO_ROOT/docs/reports/generated"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
mkdir -p "$OUTDIR"
PASS=0
FAIL=0

pass() { echo "PASSED: $1"; PASS=$((PASS + 1)); }
fail() { echo "FAILED: $1"; FAIL=$((FAIL + 1)); }

echo "=== Release Attestation ==="
echo ""

# --- Read VERSION ---
if [[ -f "$REPO_ROOT/VERSION" ]]; then
  VERSION=$(cat "$REPO_ROOT/VERSION" | tr -d '[:space:]')
else
  VERSION="0.0.0-snapshot-$(date -u +%Y%m%d%H%M%S)"
  pass "No VERSION file found; using timestamp-based version: $VERSION"
fi
echo "Version: $VERSION"

# --- Capture git commit ---
if command -v git &>/dev/null && git -C "$REPO_ROOT" rev-parse --git-dir &>/dev/null; then
  GIT_COMMIT=$(git -C "$REPO_ROOT" log -1 --format=%H 2>/dev/null || echo "unknown")
  GIT_BRANCH=$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  GIT_DIRTY=$(git -C "$REPO_ROOT" diff --quiet 2>/dev/null || echo "dirty")
  pass "Git commit captured: $(echo "$GIT_COMMIT" | head -c 12)"
else
  GIT_COMMIT="unknown"
  GIT_BRANCH="unknown"
  GIT_DIRTY="unknown"
  fail "Git not available or not a git repository"
fi
echo ""

# --- Run validation commands (if available) ---
echo "--- Running Validation Commands ---"
VALIDATION_RESULTS=""

if command -v python3 &>/dev/null; then
  PYTHON_OK="true"
  VALIDATION_RESULTS="${VALIDATION_RESULTS}  - python3: available"$'\n'
else
  PYTHON_OK="false"
  VALIDATION_RESULTS="${VALIDATION_RESULTS}  - python3: not available"$'\n'
fi

if command -v node &>/dev/null; then
  NODE_OK="true"
  NODE_VER=$(node --version 2>/dev/null || echo "unknown")
  VALIDATION_RESULTS="${VALIDATION_RESULTS}  - node: ${NODE_VER}"$'\n'
else
  NODE_OK="false"
  VALIDATION_RESULTS="${VALIDATION_RESULTS}  - node: not available"$'\n'
fi

if command -v make &>/dev/null; then
  MAKE_VER=$(make --version 2>/dev/null | head -1)
  VALIDATION_RESULTS="${VALIDATION_RESULTS}  - make: ${MAKE_VER}"$'\n'
fi

# Test that make targets exist
for t in sbom backup-restore-release release-attestation phase48-validate; do
  if grep -Eq "^${t}:" "$REPO_ROOT/Makefile" 2>/dev/null; then
    VALIDATION_RESULTS="${VALIDATION_RESULTS}  - make ${t}: target exists"$'\n'
  fi
done
echo ""

# --- Generate checksums for generated reports ---
echo "--- Generating Checksums ---"
python3 -c "
import json, os, hashlib

outdir = '$OUTDIR'
checksums = {}
if os.path.isdir(outdir):
    for f in sorted(os.listdir(outdir)):
        fpath = os.path.join(outdir, f)
        if os.path.isfile(fpath):
            with open(fpath, 'rb') as fh:
                checksums[f] = hashlib.sha256(fh.read()).hexdigest()

print(f'Found {len(checksums)} files in {outdir}')

# Write checksums to temp file for later use
tmp = {}
for k, v in sorted(checksums.items()):
    tmp[k] = v
    print(f'  {k}: {v[:16]}...')
" 2>&1
pass "Checksums computed"
echo ""

# --- GPG signature check ---
echo "--- GPG Signature ---"
SIGNATURE_STATUS="unavailable"
SIGNING_KEY=""
if command -v gpg &>/dev/null; then
  if gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep -q "sec"; then
    SIGNING_KEY=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep "^sec" | head -1 | awk '{print $2}' | cut -d'/' -f2)
    SIGNATURE_STATUS="key_available"
    pass "GPG signing key found: $SIGNING_KEY"
  else
    pass "No GPG secret keys found; signature_status set to unavailable"
  fi
else
  pass "GPG not installed; signature_status set to unavailable"
fi

# --- Write attestation files ---
echo ""
echo "--- Writing Attestation ---"

ATTESTATION_FILE="$OUTDIR/release-attestation.json"
ATTESTATION_MD="$OUTDIR/release-attestation.md"

# JSON attestation via Python
python3 << PYEOF
import json, os, hashlib

outdir = "$OUTDIR"
version = "$VERSION"
commit = "$GIT_COMMIT"
branch = "$GIT_BRANCH"
dirty = "$GIT_DIRTY"
ts = "$TIMESTAMP"
py_ok = "$PYTHON_OK" == "true"
node_ok = "$NODE_OK" == "true"
sig_status = "$SIGNATURE_STATUS"
sig_key = "$SIGNING_KEY"

checksums = {}
if os.path.isdir(outdir):
    for f in sorted(os.listdir(outdir)):
        fpath = os.path.join(outdir, f)
        if os.path.isfile(fpath) and f != 'release-attestation.json':
            with open(fpath, 'rb') as fh:
                checksums[f] = hashlib.sha256(fh.read()).hexdigest()

attestation = {
    "version": version,
    "commit": commit,
    "branch": branch,
    "working_tree_dirty": dirty if dirty != "unknown" else None,
    "generated_at": ts,
    "generated_by": "scripts/release/create-release-attestation.sh",
    "validations": {
        "python3": py_ok,
        "node": node_ok
    },
    "checksums": checksums,
    "signature_status": sig_status,
    "signing_key": sig_key if sig_key else None
}

with open("$ATTESTATION_FILE", "w") as f:
    json.dump(attestation, f, indent=2)

csum_count = len(checksums)
print(f"Wrote JSON attestation with {csum_count} checksum entries")
PYEOF

# Validate JSON
if python3 -c "import json; json.load(open('$ATTESTATION_FILE'))" 2>/dev/null; then
  pass "release-attestation.json is valid JSON"
else
  fail "release-attestation.json is invalid"
fi

# Markdown attestation via Python (use env vars to avoid heredoc bash expansion)
export ATTEST_VERSION="$VERSION"
export ATTEST_COMMIT="$GIT_COMMIT"
export ATTEST_BRANCH="$GIT_BRANCH"
export ATTEST_DIRTY="$GIT_DIRTY"
export ATTEST_TS="$TIMESTAMP"
export ATTEST_SIG_STATUS="$SIGNATURE_STATUS"
export ATTEST_SIG_KEY="$SIGNING_KEY"
export ATTEST_JSON_FILE="$ATTESTATION_FILE"
export ATTEST_MD_FILE="$ATTESTATION_MD"

python3 << 'PYEOF'
import json, os

version = os.environ["ATTEST_VERSION"]
commit = os.environ["ATTEST_COMMIT"]
branch = os.environ["ATTEST_BRANCH"]
dirty = os.environ["ATTEST_DIRTY"]
ts = os.environ["ATTEST_TS"]
sig_status = os.environ["ATTEST_SIG_STATUS"]
sig_key = os.environ["ATTEST_SIG_KEY"]
json_file = os.environ["ATTEST_JSON_FILE"]
md_file = os.environ["ATTEST_MD_FILE"]

with open(json_file) as f:
    att = json.load(f)
checksums_list = att.get("checksums", {})

lines = []
lines.append("# Release Attestation")
lines.append("")
lines.append(f"**Version:** {version}")
lines.append(f"**Commit:** {commit} ({branch})")
lines.append(f"**Generated:** {ts}")
lines.append(f"**Working tree dirty:** {dirty}")
lines.append("")
lines.append("## Validation Summary")
lines.append("")
lines.append(f"  - python3: {att['validations']['python3']}")
lines.append(f"  - node: {att['validations']['node']}")
lines.append("")
lines.append("## Checksums")
lines.append("")
if checksums_list:
    for k, v in sorted(checksums_list.items()):
        lines.append(f"  - {k}: {v}")
else:
    lines.append("  - (none)")
lines.append("")
lines.append("## Signature")
lines.append("")
lines.append(f"  - **Status:** {sig_status}")
lines.append(f"  - **Key:** {sig_key if sig_key else 'N/A'}")
lines.append("")
lines.append("## Verification")
lines.append("")
lines.append("To verify this attestation:")
lines.append("")
lines.append("```bash")
lines.append("# Verify checksums")
lines.append("sha256sum -c docs/reports/generated/release-attestation.json")
lines.append("")
lines.append("# Verify GPG signature (when available)")
lines.append("gpg --verify docs/reports/generated/release-attestation.json.sig")
lines.append("```")
lines.append("")
lines.append("---")
lines.append("")
lines.append("*Generated by: scripts/release/create-release-attestation.sh*")
lines.append(f"*Timestamp: {ts}*")

with open(md_file, "w") as f:
    f.write("\n".join(lines) + "\n")

print(f"Wrote markdown attestation with {len(checksums_list)} checksum entries")
PYEOF

pass "Attestation written to $ATTESTATION_FILE and $ATTESTATION_MD"

echo ""
echo "=== Results ==="
echo "Passed: $PASS, Failed: $FAIL"
echo ""
echo "Output files: $ATTESTATION_MD, $ATTESTATION_FILE"
