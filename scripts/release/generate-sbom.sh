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

echo "=== SBOM Generation ==="
echo ""

# --- Frontend SBOM ---
echo "--- Frontend SBOM ---"
FRONTEND_SBOM="$OUTDIR/sbom-frontend.json"
LOCKFILE="$REPO_ROOT/frontend/package-lock.json"

if [[ -f "$LOCKFILE" ]]; then
  python3 -c "
import json, sys

lockfile = '$LOCKFILE'
outfile = '$FRONTEND_SBOM'
ts = '$TIMESTAMP'

try:
    with open(lockfile) as f:
        data = json.load(f)
except (json.JSONDecodeError, FileNotFoundError) as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)

pkgs = data.get('packages', {})
entries = []
for path, info in sorted(pkgs.items()):
    if path == '':
        continue
    name = path.split('node_modules/')[-1] if 'node_modules/' in path else path
    ver = info.get('version', 'unknown')
    entries.append({'name': name, 'version': ver})

sbom = {
    'source': 'frontend/package-lock.json',
    'generated_at': ts,
    'dependencies': entries,
    'count': len(entries)
}

with open(outfile, 'w') as f:
    json.dump(sbom, f, indent=2)

print(f'Found {len(entries)} frontend dependencies')
"
  if python3 -c "import json; json.load(open('$FRONTEND_SBOM'))" 2>/dev/null; then
    pass "sbom-frontend.json generated ($(wc -l < "$FRONTEND_SBOM") lines)"
  else
    fail "sbom-frontend.json generated but invalid JSON"
  fi
else
  echo '{ "source": "frontend/package-lock.json", "warning": "package-lock.json not found", "dependencies": [], "count": 0 }' > "$FRONTEND_SBOM"
  pass "sbom-frontend.json written with warning (package-lock.json not found)"
fi

# --- Backend SBOM ---
echo ""
echo "--- Backend SBOM ---"
BACKEND_SBOM="$OUTDIR/sbom-backend.txt"

if command -v python3 &>/dev/null; then
  python3 -c "
import sys
from importlib.metadata import distributions

outfile = '$BACKEND_SBOM'
ts = '$TIMESTAMP'

dists = sorted(
    [(d.metadata.get('Name', d.name), d.version) for d in distributions()],
    key=lambda x: x[0].lower()
)

with open(outfile, 'w') as f:
    f.write('Backend Python Dependencies (pip)\n')
    f.write(f'Generated: {ts}\n')
    f.write(f'Python: {sys.version}\n')
    f.write('-' * 60 + '\n')
    for name, version in dists:
        f.write(f'{name}=={version}\n')

print(f'Found {len(dists)} backend packages')
"
  if [[ -f "$BACKEND_SBOM" ]]; then
    pass "sbom-backend.txt generated ($(wc -l < "$BACKEND_SBOM") lines)"
  else
    fail "sbom-backend.txt not created"
  fi
else
  echo "Backend SBOM: python3 not available" > "$BACKEND_SBOM"
  fail "python3 required for backend SBOM"
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS, Failed: $FAIL"
echo ""
echo "Output files:"
echo "  $FRONTEND_SBOM"
echo "  $BACKEND_SBOM"
