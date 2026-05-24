# Next Prompt · PHASE 24

Repository target: `cvsz/zdash`

Prompt/document target path:

`docs/prompt/PHASE_24_AUTONOMOUS_CERTIFICATION_AUDITOR_PORTAL_ENTERPRISE_PACK.md`

```text
Continue from the previous zDash implementation.

Repository target:

cvsz/zdash

Prompt/document target path:

docs/prompt/PHASE_24_AUTONOMOUS_CERTIFICATION_AUDITOR_PORTAL_ENTERPRISE_PACK.md

Project:

⬡ zDash · FULL SYSTEM BLUEPRINT v2.0

Now execute ONLY:

PHASE 24 · AUTONOMOUS CERTIFICATION + EXTERNAL AUDITOR PORTAL + ENTERPRISE CUSTOMER DEPLOYMENT PACKS
Certification Engine + Auditor Workspace + Evidence Portal + Customer Deployment Packs + Release Attestation

IMPORTANT:
Before coding, inspect the existing repository.

The repository may include Phase 1–23 modules, or some intermediate modules may be missing.
Do not rebuild existing modules from scratch.
Do not remove existing behavior.
If a dependency from Phase 11–23 is missing, create a safe compatibility shim or minimal adapter interface.

This phase must make zDash easier to certify, audit, package, and deploy for enterprise customers.
It must not enable live trading, real IoT actions, real social posting, secret access, unsafe plugin execution, or unreviewed automation by default.

============================================================
PHASE 24 OBJECTIVE
============================================================

Build the autonomous certification and enterprise deployment pack layer for zDash.

Main goals:

1. Add autonomous certification engine
2. Add certification control catalog
3. Add certification test runner
4. Add release attestation system
5. Add external auditor portal backend APIs
6. Add auditor read-only workspace
7. Add evidence request workflow
8. Add evidence redaction and approval workflow
9. Add enterprise customer deployment pack generator
10. Add signed deployment manifest
11. Add customer handoff bundle generator
12. Add environment readiness validator
13. Add security baseline checker
14. Add compliance scorecard
15. Add frontend pages for Certification, Auditor Portal, Deployment Packs
16. Add tests for certification, auditor access, redaction, deployment pack safety, and tenant isolation

Critical safety rule:
Certification and deployment tooling must be read-only or dry-run by default.
No generated deployment pack may include secrets unless explicitly requested by an admin with typed confirmation.
Auditor users must never access secrets, billing secrets, provider tokens, raw credentials, private keys, or cross-tenant data.

============================================================
ASSUMED EXISTING CORE MODULES
============================================================

The system may already include:

- FastAPI backend
- React/Vite frontend
- Auth/JWT
- RBAC
- Multi-tenant organizations/workspaces
- Audit logs
- Scheduler
- Worker queue
- Risk Guardian
- Backtesting
- Content pipeline
- Marketplace plugins
- Billing and entitlements
- Notifications
- Metrics
- Docker/Kubernetes/Terraform templates
- Governance policy engine
- Compliance evidence collector
- Disaster recovery module
- Incident command center
- Risk register
- Runbook executor

If present, integrate with them.
If missing, create safe adapter interfaces.

============================================================
PHASE 24 MODULES TO ADD
============================================================

Create backend modules:

backend/app/certification/
  __init__.py
  models.py
  control_catalog.py
  certification_runner.py
  scorecard.py
  attestation.py
  certification_service.py

backend/app/auditor/
  __init__.py
  models.py
  auditor_service.py
  evidence_request_service.py
  redaction.py
  access_policy.py

backend/app/deployment_packs/
  __init__.py
  models.py
  manifest.py
  pack_builder.py
  readiness_validator.py
  security_baseline.py
  handoff_bundle.py
  deployment_pack_service.py

backend/app/api/certification.py
backend/app/api/auditor.py
backend/app/api/deployment_packs.py

Create frontend modules:

frontend/src/pages/Certification.tsx
frontend/src/pages/AuditorPortal.tsx
frontend/src/pages/DeploymentPacks.tsx

frontend/src/components/certification/
  CertificationStatusCard.tsx
  ControlCatalogTable.tsx
  CertificationRunPanel.tsx
  ComplianceScorecard.tsx
  ReleaseAttestationPanel.tsx

frontend/src/components/auditor/
  AuditorWorkspace.tsx
  EvidenceRequestTable.tsx
  EvidenceReviewPanel.tsx
  RedactionPreview.tsx
  AuditorAccessSummary.tsx

frontend/src/components/deploymentPacks/
  DeploymentPackBuilder.tsx
  DeploymentManifestPanel.tsx
  ReadinessCheckTable.tsx
  SecurityBaselinePanel.tsx
  CustomerHandoffPanel.tsx

frontend/src/hooks/useCertification.ts
frontend/src/hooks/useAuditor.ts
frontend/src/hooks/useDeploymentPacks.ts

Create docs:

docs/architecture/PHASE_24_CERTIFICATION_AUDITOR_DEPLOYMENT_PACKS.md
docs/runbooks/CERTIFICATION_RUNBOOK.md
docs/runbooks/AUDITOR_PORTAL_RUNBOOK.md
docs/runbooks/ENTERPRISE_DEPLOYMENT_PACK_RUNBOOK.md

Update:

backend/app/main.py
backend/app/core/config.py
backend/app/core/events.py
backend/app/auth/rbac.py
backend/app/audit/audit_service.py

frontend/src/App.tsx
frontend/src/api/types.ts
frontend/src/api/endpoints.ts
frontend/src/components/layout/Sidebar.tsx
frontend/src/pages/Settings.tsx

README.md
.env.example

Also create this prompt file:

docs/prompt/PHASE_24_AUTONOMOUS_CERTIFICATION_AUDITOR_PORTAL_ENTERPRISE_PACK.md

The prompt file must contain this Phase 24 implementation prompt so future agents can continue from it.

============================================================
CONFIG REQUIREMENTS
============================================================

Update `.env.example`:

CERTIFICATION_ENABLED=true
CERTIFICATION_AUTORUN_ENABLED=false
CERTIFICATION_FAIL_CLOSED=true
CERTIFICATION_DEFAULT_FRAMEWORK=zdash_enterprise_baseline
CERTIFICATION_REQUIRE_ATTESTATION_APPROVAL=true

AUDITOR_PORTAL_ENABLED=true
AUDITOR_READ_ONLY=true
AUDITOR_REQUIRE_EVIDENCE_APPROVAL=true
AUDITOR_ALLOW_DOWNLOADS=false
AUDITOR_SESSION_EXPIRE_MINUTES=60

EVIDENCE_REDACTION_ENABLED=true
EVIDENCE_REDACTION_STRICT=true
EVIDENCE_EXPORT_INCLUDE_SECRETS=false

DEPLOYMENT_PACKS_ENABLED=true
DEPLOYMENT_PACK_DRY_RUN=true
DEPLOYMENT_PACK_INCLUDE_SECRETS=false
DEPLOYMENT_PACK_REQUIRE_ADMIN_APPROVAL=true
DEPLOYMENT_PACK_OUTPUT_DIR=backend/data/deployment_packs

RELEASE_ATTESTATION_ENABLED=true
RELEASE_ATTESTATION_REQUIRE_SIGNOFF=true
RELEASE_ATTESTATION_SIGNING_MODE=mock

SECURITY_BASELINE_ENABLED=true
READINESS_VALIDATOR_ENABLED=true

Rules:

- Certification fail-closed must be true by default.
- Auditor portal must be read-only by default.
- Evidence redaction must be strict by default.
- Deployment packs must be dry-run by default.
- Deployment packs must exclude secrets by default.
- Release signing must use mock/local mode unless explicitly configured.
- No secret may be logged, exposed in frontend, included in auditor views, or exported by default.

============================================================
CERTIFICATION MODELS
============================================================

Create Pydantic models:

1. CertificationFramework

Fields:
- id
- name
- version
- description
- controls
- created_at
- updated_at

2. CertificationControl

Fields:
- id
- framework_id
- control_code
- title
- category
- description
- severity
- evidence_required
- automated_check
- manual_review_required
- enabled

Categories:
- access_control
- tenant_isolation
- audit_logging
- risk_management
- trading_safety
- content_safety
- iot_safety
- secret_management
- disaster_recovery
- incident_response
- marketplace_safety
- billing_safety
- deployment_security
- governance

Severity:
- low
- medium
- high
- critical

3. CertificationCheckResult

Fields:
- control_id
- status
- score
- message
- evidence_ids
- findings
- remediation
- checked_at

Status:
- passed
- failed
- warning
- not_applicable
- manual_review_required

4. CertificationRun

Fields:
- id
- organization_id
- workspace_id
- framework_id
- status
- score
- passed_controls
- failed_controls
- warning_controls
- manual_review_controls
- results
- started_at
- finished_at
- duration_ms

5. ComplianceScorecard

Fields:
- organization_id
- workspace_id
- framework_id
- total_score
- category_scores
- critical_failures
- warnings
- generated_at

6. ReleaseAttestation

Fields:
- id
- organization_id
- workspace_id
- release_version
- git_commit
- image_tag
- certification_run_id
- safety_summary
- approved_by
- approved_at
- signature
- signing_mode
- status
- created_at

============================================================
CERTIFICATION ENGINE REQUIREMENTS
============================================================

Create:

backend/app/certification/control_catalog.py

Implement default framework:

zdash_enterprise_baseline

Required controls:

- RBAC enabled
- Default admin password changed in production
- JWT secret not default in production
- Tenant isolation enabled
- Cross-tenant access blocked
- Audit logging enabled
- Metrics enabled without secrets
- DRY_RUN true by default
- Live trading blocked by default
- Guardian risk system enabled
- Emergency kill switch configured
- Real IoT blocked by default
- Social posting approval required
- Marketplace plugin secret access blocked by default
- Plugin external network blocked by default
- Billing does not store raw card data
- Evidence export excludes secrets
- Auditor portal read-only
- Backup verification enabled
- Restore drill dry-run by default
- Runbook executor dry-run by default
- Deployment pack excludes secrets by default
- Production safety checker passes

Create:

backend/app/certification/certification_runner.py

Methods:

- run_framework(framework_id, context) -> CertificationRun
- run_control(control_id, context) -> CertificationCheckResult
- collect_findings(result) -> list[dict]

Rules:
- Checks must be deterministic.
- Missing module must produce warning or manual_review_required, not crash.
- Critical safety controls must fail if unsafe config is detected.
- Live trading, real IoT, real social posting, and secret export must fail unless explicitly configured and approved.

Create:

backend/app/certification/scorecard.py

Methods:

- build_scorecard(certification_run) -> ComplianceScorecard
- calculate_category_scores(results) -> dict
- list_critical_failures(results) -> list[dict]

Create:

backend/app/certification/attestation.py

Methods:

- create_release_attestation(request, certification_run_id)
- approve_attestation(attestation_id, approved_by)
- generate_signature(payload)
- verify_signature(attestation_id)

Rules:
- Mock signing mode allowed for local dev.
- Real signing must be pluggable.
- Attestation must not include secrets.
- Approval required when RELEASE_ATTESTATION_REQUIRE_SIGNOFF=true.

============================================================
AUDITOR PORTAL REQUIREMENTS
============================================================

Create:

backend/app/auditor/models.py

Models:

1. AuditorWorkspace

Fields:
- id
- organization_id
- workspace_id
- name
- auditor_email
- status
- read_only
- expires_at
- created_by
- created_at
- updated_at

2. EvidenceRequest

Fields:
- id
- organization_id
- workspace_id
- auditor_workspace_id
- requested_by
- title
- description
- evidence_types
- status
- response
- created_at
- updated_at
- fulfilled_at

Status:
- open
- in_review
- approved
- rejected
- fulfilled
- expired

3. RedactionResult

Fields:
- ok
- redacted_payload
- redacted_fields
- warnings
- blocked
- reason

Create:

backend/app/auditor/redaction.py

Redact:

- API keys
- access tokens
- refresh tokens
- passwords
- private keys
- SSH keys
- broker credentials
- Cloudflare tokens
- Stripe keys
- SMTP passwords
- webhook secrets
- JWT secrets
- database URLs with passwords

Rules:
- Strict redaction enabled by default.
- Redaction must run before auditor response.
- If uncertain, redact.
- Auditor download disabled by default.
- Auditor access must be tenant-scoped and read-only.

Create:

backend/app/auditor/access_policy.py

Rules:
- Auditor can read approved evidence only.
- Auditor cannot create, update, delete, execute, approve, publish, deploy, restore, or export secrets.
- Auditor cannot access other tenants.
- Auditor cannot access raw logs if they contain potential secrets.
- Auditor cannot view billing provider secrets.

============================================================
DEPLOYMENT PACK REQUIREMENTS
============================================================

Create:

backend/app/deployment_packs/models.py

Models:

1. DeploymentPackRequest

Fields:
- organization_id
- workspace_id
- target_environment
- include_docker
- include_kubernetes
- include_terraform
- include_cloudflare
- include_runbooks
- include_evidence
- include_secrets
- confirmation
- metadata

2. DeploymentPack

Fields:
- id
- organization_id
- workspace_id
- target_environment
- status
- manifest
- file_path
- size_bytes
- checksum
- warnings
- created_by
- created_at
- completed_at

3. DeploymentManifest

Fields:
- id
- app_name
- release_version
- git_commit
- image_tags
- required_env
- required_secrets
- safety_defaults
- included_components
- generated_at

4. ReadinessCheck

Fields:
- id
- name
- category
- status
- message
- remediation
- checked_at

5. SecurityBaselineResult

Fields:
- score
- checks
- blockers
- warnings
- generated_at

Create:

backend/app/deployment_packs/readiness_validator.py

Validate:

- required env vars present
- default secrets rejected in production
- DRY_RUN remains true by default
- Guardian enabled
- social approval required
- IoT confirmation required
- CORS safe
- database reachable if configured
- Redis reachable if configured
- migration status
- backup config
- metrics config
- auditor portal read-only
- deployment pack excludes secrets by default

Create:

backend/app/deployment_packs/security_baseline.py

Check:

- no default JWT secret in production
- no default admin password in production
- no wildcard CORS with credentials
- no secret exposure in frontend env
- no raw card storage
- no plugin secret access by default
- no live trading by default
- no real IoT by default
- no real social posting by default
- restore dry-run by default

Create:

backend/app/deployment_packs/pack_builder.py

Build a dry-run or real bundle containing:

- manifest.json
- README_DEPLOYMENT.md
- .env.example
- docker-compose files if present
- k8s manifests if present
- terraform templates if present
- Cloudflare templates if present
- runbooks if present
- certification summary if present
- compliance evidence summary if approved
- release attestation if present

Rules:
- Exclude secrets by default.
- include_secrets requires:
  - admin permission
  - confirmation == "CONFIRM_SECRET_PACK"
  - DEPLOYMENT_PACK_INCLUDE_SECRETS=true
- Never include raw payment data.
- Never include private keys by default.
- Generate checksum.
- Generate manifest.
- Emit audit event.

============================================================
API REQUIREMENTS
============================================================

Certification API:

GET /api/certification/status
GET /api/certification/frameworks
GET /api/certification/controls
POST /api/certification/run
GET /api/certification/runs
GET /api/certification/runs/{run_id}
GET /api/certification/runs/{run_id}/scorecard
POST /api/certification/attestations
GET /api/certification/attestations
POST /api/certification/attestations/{attestation_id}/approve
POST /api/certification/attestations/{attestation_id}/verify

Auditor API:

GET /api/auditor/status
GET /api/auditor/workspaces
POST /api/auditor/workspaces
PATCH /api/auditor/workspaces/{workspace_id}
GET /api/auditor/evidence-requests
POST /api/auditor/evidence-requests
PATCH /api/auditor/evidence-requests/{request_id}
POST /api/auditor/evidence-requests/{request_id}/approve
POST /api/auditor/evidence-requests/{request_id}/reject
GET /api/auditor/evidence-requests/{request_id}/response
POST /api/auditor/redact-preview

Deployment Pack API:

GET /api/deployment-packs/status
POST /api/deployment-packs/readiness-check
POST /api/deployment-packs/security-baseline
POST /api/deployment-packs/build
GET /api/deployment-packs
GET /api/deployment-packs/{pack_id}
GET /api/deployment-packs/{pack_id}/manifest

All endpoints must use standard API response shape:

{
  "ok": true,
  "data": {},
  "error": null,
  "timestamp": "ISO_DATE"
}

Errors:

{
  "ok": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  },
  "timestamp": "ISO_DATE"
}

Required error codes:

- CERTIFICATION_FAILED
- CONTROL_NOT_FOUND
- ATTESTATION_NOT_APPROVED
- AUDITOR_ACCESS_DENIED
- EVIDENCE_NOT_APPROVED
- REDACTION_REQUIRED
- DEPLOYMENT_PACK_BLOCKED
- SECRET_PACK_NOT_ALLOWED
- READINESS_CHECK_FAILED
- TENANT_ACCESS_DENIED

============================================================
RBAC REQUIREMENTS
============================================================

Add permissions:

Certification:
- certification.read
- certification.run
- certification.attest
- certification.approve_attestation

Auditor:
- auditor.read
- auditor.manage
- auditor.evidence.request
- auditor.evidence.approve
- auditor.redaction.preview

Deployment packs:
- deployment_pack.read
- deployment_pack.build
- deployment_pack.include_secrets
- deployment_pack.download

Role mapping:

admin:
- all permissions

operator:
- certification.read
- certification.run
- auditor.read
- auditor.evidence.approve
- deployment_pack.read
- deployment_pack.build

analyst:
- certification.read
- auditor.read
- deployment_pack.read

viewer:
- certification.read limited
- auditor.read limited
- deployment_pack.read limited

auditor:
- auditor.read
- auditor.evidence.request
- certification.read limited
- deployment_pack.read limited

Rules:
- Add auditor role if RBAC supports role extension.
- Auditor role must be read-only.
- Auditor cannot build deployment packs.
- Auditor cannot approve evidence.
- Auditor cannot access secrets.

============================================================
EVENT TYPES
============================================================

Add events:

Certification:
- certification.framework.loaded
- certification.control.checked
- certification.run.started
- certification.run.completed
- certification.run.failed
- certification.scorecard.generated
- certification.attestation.created
- certification.attestation.approved
- certification.attestation.verified
- certification.attestation.failed

Auditor:
- auditor.workspace.created
- auditor.workspace.updated
- auditor.evidence.requested
- auditor.evidence.approved
- auditor.evidence.rejected
- auditor.evidence.fulfilled
- auditor.redaction.applied
- auditor.access.blocked

Deployment packs:
- deployment_pack.readiness.checked
- deployment_pack.security_baseline.checked
- deployment_pack.build.started
- deployment_pack.build.completed
- deployment_pack.build.blocked
- deployment_pack.manifest.generated
- deployment_pack.secret_inclusion.blocked

============================================================
FRONTEND REQUIREMENTS
============================================================

Add sidebar pages:

- Certification
- Auditor Portal
- Deployment Packs

Certification page must show:
- Certification status
- Framework selector
- Control catalog table
- Run certification button
- Latest certification runs
- Compliance scorecard
- Critical failures
- Release attestation panel

Auditor Portal page must show:
- Auditor workspace list
- Create auditor workspace form
- Evidence request table
- Evidence review and approval panel
- Redaction preview panel
- Read-only access summary

Deployment Packs page must show:
- Readiness validation panel
- Security baseline panel
- Deployment pack builder
- Manifest preview
- Customer handoff bundle panel
- Warnings and blockers
- Secret inclusion blocked by default

Safety:
- Secret inclusion requires typed confirmation:
  CONFIRM_SECRET_PACK
- Auditor download disabled unless enabled.
- Auditor UI must be visibly read-only.
- Deployment pack UI must clearly label dry-run state.
- Attestation approval must require confirmation.

============================================================
TEST REQUIREMENTS
============================================================

Create backend tests:

backend/app/tests/test_certification_models.py
backend/app/tests/test_control_catalog.py
backend/app/tests/test_certification_runner.py
backend/app/tests/test_compliance_scorecard.py
backend/app/tests/test_release_attestation.py
backend/app/tests/test_certification_api.py

backend/app/tests/test_auditor_models.py
backend/app/tests/test_auditor_redaction.py
backend/app/tests/test_auditor_access_policy.py
backend/app/tests/test_evidence_request_service.py
backend/app/tests/test_auditor_api.py

backend/app/tests/test_deployment_pack_models.py
backend/app/tests/test_readiness_validator.py
backend/app/tests/test_security_baseline.py
backend/app/tests/test_deployment_pack_builder.py
backend/app/tests/test_deployment_pack_api.py

backend/app/tests/test_phase24_tenant_isolation.py

Test:
- default certification framework loads
- critical safety controls exist
- live trading blocked control passes only when blocked
- real IoT blocked control passes only when blocked
- real social posting blocked control passes only when blocked
- secret export blocked control passes only when blocked
- missing module produces warning/manual review, not crash
- scorecard calculates category scores
- attestation excludes secrets
- attestation approval required
- redaction removes tokens/passwords/private keys
- auditor cannot access raw secrets
- auditor is read-only
- evidence approval workflow works
- deployment pack excludes secrets by default
- secret pack requires confirmation
- readiness validator detects default production secrets
- security baseline detects unsafe CORS
- deployment manifest generated
- tenant A cannot read tenant B certification/auditor/deployment packs
- API endpoints return standard response shape

Create frontend tests:

frontend/src/tests/Certification.test.tsx
frontend/src/tests/AuditorPortal.test.tsx
frontend/src/tests/DeploymentPacks.test.tsx

Test:
- Certification page renders controls
- Run certification button appears
- Scorecard appears
- Attestation panel appears
- Auditor portal shows read-only banner
- Evidence requests render
- Redaction preview appears
- Deployment packs page renders readiness checks
- Secret pack requires typed confirmation
- Manifest panel renders

All tests must pass:

Backend:

cd backend
pytest

Frontend:

cd frontend
npm test
npm run build

============================================================
README UPDATE REQUIREMENTS
============================================================

Update README with:

- Phase 24 overview
- Autonomous certification engine
- Control catalog
- Compliance scorecard
- Release attestation
- External auditor portal
- Evidence request workflow
- Redaction system
- Deployment pack builder
- Readiness validator
- Security baseline checker
- Customer handoff bundle
- API examples
- Frontend pages
- Test commands
- Safety checklist

Add curl examples:

Certification status:

curl http://localhost:8000/api/certification/status \
  -H "Authorization: Bearer TOKEN"

Run certification:

curl -X POST http://localhost:8000/api/certification/run \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "framework_id": "zdash_enterprise_baseline"
  }'

Create auditor workspace:

curl -X POST http://localhost:8000/api/auditor/workspaces \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "External SOC2 Auditor",
    "auditor_email": "auditor@example.com",
    "expires_at": "2026-12-31T23:59:59Z"
  }'

Run readiness check:

curl -X POST http://localhost:8000/api/deployment-packs/readiness-check \
  -H "Authorization: Bearer TOKEN"

Build dry-run deployment pack:

curl -X POST http://localhost:8000/api/deployment-packs/build \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_environment": "production",
    "include_docker": true,
    "include_kubernetes": true,
    "include_terraform": true,
    "include_cloudflare": true,
    "include_runbooks": true,
    "include_evidence": true,
    "include_secrets": false,
    "confirmation": ""
  }'

============================================================
ACCEPTANCE CRITERIA
============================================================

Phase 24 is complete only when:

- Certification module exists.
- Default certification framework exists.
- Certification runner works.
- Compliance scorecard works.
- Release attestation works.
- Auditor portal module exists.
- Evidence request workflow works.
- Redaction system works.
- Auditor access is read-only.
- Deployment pack module exists.
- Readiness validator works.
- Security baseline checker works.
- Deployment manifest is generated.
- Deployment pack excludes secrets by default.
- API endpoints work.
- Frontend Certification page works.
- Frontend Auditor Portal page works.
- Frontend Deployment Packs page works.
- RBAC protects sensitive actions.
- Tenant isolation is enforced.
- Event logs are emitted.
- Audit logs are created.
- Existing Phase 1–23 behavior remains intact.
- Existing tests still pass.
- New Phase 24 tests pass.
- No live trading is enabled by default.
- No real IoT action is enabled by default.
- No real social posting is enabled by default.
- No secret export or secret deployment pack is allowed without explicit confirmation.
- README includes Phase 24 documentation.
- Prompt file exists at docs/prompt/PHASE_24_AUTONOMOUS_CERTIFICATION_AUDITOR_PORTAL_ENTERPRISE_PACK.md

============================================================
DELIVERABLE FORMAT
============================================================

Generate:

1. Repository inspection summary
2. Folder tree changes
3. Full source code for every new backend file
4. Full source code for every new frontend file
5. Full patched code for every updated file
6. Test files
7. .env.example updates
8. README updates
9. docs/prompt Phase 24 prompt file
10. API examples
11. Run instructions
12. Test instructions
13. Safety checklist
14. Acceptance checklist
15. Known limitations
16. Phase 25 handoff notes

============================================================
IMPORTANT IMPLEMENTATION RULES
============================================================

- Do not use pseudocode.
- Do not skip files.
- Do not remove existing behavior.
- Keep existing backend tests passing.
- Keep existing frontend tests passing.
- Detect missing intermediate modules and add safe shims.
- Use typed Python where reasonable.
- Use TypeScript types.
- Never hardcode credentials.
- Never expose secrets in frontend.
- Never log secrets.
- Never include secrets in auditor views.
- Never include secrets in deployment packs by default.
- Never enable live trading by default.
- Never enable real social posting by default.
- Never enable real IoT power actions by default.
- Never bypass Guardian risk checks.
- Never bypass content approval checks.
- Never bypass tenant isolation.
- Never bypass RBAC.
- Auditor portal must be read-only.
- Certification must fail closed for critical safety controls.
- Deployment pack generation must be dry-run and secret-free by default.
- Keep implementation modular enough for Phase 25 customer cloud installer, managed update channel, and enterprise SLA automation.

Now generate the complete Phase 24 implementation and save this prompt into:

docs/prompt/PHASE_24_AUTONOMOUS_CERTIFICATION_AUDITOR_PORTAL_ENTERPRISE_PACK.md
```
