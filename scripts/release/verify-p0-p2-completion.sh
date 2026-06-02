#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PASS=0
FAIL=0
ERRORS=""

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); ERRORS="$ERRORS  - $1\n"; }

echo "=== Phase 48 P0-P2 Completion Validation ==="
echo ""

# 1. backend/app/backtesting/models.py has Field(default_factory=dict) for parameter_grid
echo "--- Backend: OptimizationRequest parameter_grid ---"
MODELS_FILE="$REPO_ROOT/backend/app/backtesting/models.py"
if [[ -f "$MODELS_FILE" ]]; then
  if grep -q "parameter_grid.*dict\[str.*Field(default_factory=dict)" "$MODELS_FILE" || \
     grep -q "parameter_grid.*Field(default_factory=dict)" "$MODELS_FILE"; then
    pass "models.py has Field(default_factory=dict) for parameter_grid"
  else
    fail "models.py missing Field(default_factory=dict) for parameter_grid"
  fi
else
  fail "models.py not found"
fi

# 2. frontend/src/api/endpoints.ts normalizes parameter_grid in runOptimization
echo ""
echo "--- Frontend: runOptimization parameter_grid normalization ---"
ENDPOINTS_FILE="$REPO_ROOT/frontend/src/api/endpoints.ts"
if [[ -f "$ENDPOINTS_FILE" ]]; then
  if grep -q "parameter_grid" "$ENDPOINTS_FILE" && grep -q "normalizedPayload" "$ENDPOINTS_FILE"; then
    pass "endpoints.ts normalizes parameter_grid in runOptimization"
  else
    fail "endpoints.ts runOptimization missing parameter_grid normalization"
  fi
else
  fail "endpoints.ts not found"
fi

# 3. README.md mentions Phase 46, Phase 47, Phase 48
echo ""
echo "--- README: Phase mentions ---"
README_FILE="$REPO_ROOT/README.md"
if [[ -f "$README_FILE" ]]; then
  for phase in "Phase 46" "Phase 47" "Phase 48"; do
    if grep -q "$phase" "$README_FILE"; then
      pass "README.md mentions $phase"
    else
      fail "README.md does not mention $phase"
    fi
  done
else
  fail "README.md not found"
fi

# 4. docs/reports/PHASE47_REAL_TEAM_WORKSPACE_REPORT.md no longer says "N/A"
echo ""
echo "--- Phase 47 report: N/A check ---"
PHASE47_REPORT="$REPO_ROOT/docs/reports/PHASE47_REAL_TEAM_WORKSPACE_REPORT.md"
if [[ -f "$PHASE47_REPORT" ]]; then
  if grep -q "N/A" "$PHASE47_REPORT"; then
    fail "PHASE47 report still contains 'N/A'"
  else
    pass "PHASE47 report has no 'N/A' entries"
  fi
else
  fail "PHASE47 report not found"
fi

# 5. scripts/release/generate-sbom.sh exists and is executable
echo ""
echo "--- Script: generate-sbom.sh ---"
SBOM_SCRIPT="$REPO_ROOT/scripts/release/generate-sbom.sh"
if [[ -x "$SBOM_SCRIPT" ]]; then
  pass "generate-sbom.sh exists and is executable"
else
  fail "generate-sbom.sh missing or not executable"
fi

# 6. docs/ops/SLO_DEFINITIONS.md exists
echo ""
echo "--- Docs: SLO_DEFINITIONS.md ---"
if [[ -f "$REPO_ROOT/docs/ops/SLO_DEFINITIONS.md" ]]; then
  pass "SLO_DEFINITIONS.md exists"
else
  fail "SLO_DEFINITIONS.md missing"
fi

# 7. docs/runbooks/INCIDENT_RESPONSE.md exists
echo ""
echo "--- Docs: INCIDENT_RESPONSE.md ---"
if [[ -f "$REPO_ROOT/docs/runbooks/INCIDENT_RESPONSE.md" ]]; then
  pass "INCIDENT_RESPONSE.md exists"
else
  fail "INCIDENT_RESPONSE.md missing"
fi

# 8. scripts/release/backup-restore-proof.sh exists and is executable
echo ""
echo "--- Script: backup-restore-proof.sh ---"
BACKUP_SCRIPT="$REPO_ROOT/scripts/release/backup-restore-proof.sh"
if [[ -x "$BACKUP_SCRIPT" ]]; then
  pass "backup-restore-proof.sh exists and is executable"
else
  fail "backup-restore-proof.sh missing or not executable"
fi

# 9. docs/ops/DEPENDENCY_UPDATE_POLICY.md exists
echo ""
echo "--- Docs: DEPENDENCY_UPDATE_POLICY.md ---"
if [[ -f "$REPO_ROOT/docs/ops/DEPENDENCY_UPDATE_POLICY.md" ]]; then
  pass "DEPENDENCY_UPDATE_POLICY.md exists"
else
  fail "DEPENDENCY_UPDATE_POLICY.md missing"
fi

# 10. docs/ops/SIGNED_RELEASE_ATTESTATION.md exists
echo ""
echo "--- Docs: SIGNED_RELEASE_ATTESTATION.md ---"
if [[ -f "$REPO_ROOT/docs/ops/SIGNED_RELEASE_ATTESTATION.md" ]]; then
  pass "SIGNED_RELEASE_ATTESTATION.md exists"
else
  fail "SIGNED_RELEASE_ATTESTATION.md missing"
fi

# 11. scripts/release/create-release-attestation.sh exists and is executable
echo ""
echo "--- Script: create-release-attestation.sh ---"
ATTEST_SCRIPT="$REPO_ROOT/scripts/release/create-release-attestation.sh"
if [[ -x "$ATTEST_SCRIPT" ]]; then
  pass "create-release-attestation.sh exists and is executable"
else
  fail "create-release-attestation.sh missing or not executable"
fi

# 12. No .env tracked in git
echo ""
echo "--- Git: .env tracking ---"
ENV_TRACKED=$(git -C "$REPO_ROOT" ls-files '.env' 2>/dev/null || true)
if [[ -z "$ENV_TRACKED" ]]; then
  pass "No .env tracked in git"
else
  fail ".env is tracked in git: $ENV_TRACKED"
fi

# 13. No obvious secret patterns in generated reports
echo ""
echo "--- Reports: Secret pattern scan ---"
SECRET_FOUND=false
if [[ -d "$REPO_ROOT/docs/reports/generated" ]]; then
  if grep -r --include="*.json" --include="*.md" --include="*.txt" \
    -E '(sk-[A-Za-z0-9_-]{20,}|BEGIN\s+(RSA\s+)?PRIVATE\s+KEY)' \
    "$REPO_ROOT/docs/reports/generated" 2>/dev/null | grep -v "signature_status"; then
    SECRET_FOUND=true
  fi
fi
if $SECRET_FOUND; then
  fail "Secret patterns found in generated reports!"
else
  pass "No obvious secret patterns in generated reports"
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS, Failed: $FAIL"
if [[ "$FAIL" -gt 0 ]]; then
  echo ""
  echo "Errors:"
  echo -e "$ERRORS"
  exit 1
fi
