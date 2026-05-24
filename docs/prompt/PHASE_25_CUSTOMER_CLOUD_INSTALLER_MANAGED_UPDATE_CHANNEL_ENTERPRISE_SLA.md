# Next Prompt · PHASE 25

Repository target: `cvsz/zdash`

Prompt/document target path:

`docs/prompt/PHASE_25_CUSTOMER_CLOUD_INSTALLER_MANAGED_UPDATE_CHANNEL_ENTERPRISE_SLA.md`

```text
Continue from the previous zDash implementation.

Repository target:

cvsz/zdash

Prompt/document target path:

docs/prompt/PHASE_25_CUSTOMER_CLOUD_INSTALLER_MANAGED_UPDATE_CHANNEL_ENTERPRISE_SLA.md

Project:

⬡ zDash · FULL SYSTEM BLUEPRINT v2.0

Now execute ONLY:

PHASE 25 · CUSTOMER CLOUD INSTALLER + MANAGED UPDATE CHANNEL + ENTERPRISE SLA AUTOMATION
Customer Installer Wizard + Managed Releases + Update Orchestrator + SLA Monitor + Support Bundle Automation

IMPORTANT:
Before coding, inspect the existing repository.

The repository may include Phase 1–24 modules, or some intermediate modules may be missing.
Do not rebuild existing modules from scratch.
Do not remove existing behavior.
If a dependency from Phase 11–24 is missing, create a safe compatibility shim or minimal adapter interface.

This phase must make zDash easier to install, update, support, and operate for enterprise customers.
It must not enable live trading, real IoT actions, real social posting, secret access, unsafe plugin execution, unreviewed deployment, or destructive update behavior by default.

============================================================
PHASE 25 OBJECTIVE
============================================================

Build the customer cloud installer and managed operations layer for zDash.

Main goals:

1. Add customer cloud installer planning system
2. Add deployment target profiles for local VM, Docker, Kubernetes, and Cloudflare Tunnel
3. Add installer manifest generator
4. Add preflight environment validator
5. Add safe install plan generator
6. Add managed update channel model
7. Add release feed and update policy system
8. Add update orchestrator with dry-run first behavior
9. Add rollback planner and rollback validation
10. Add SLA monitor and uptime/error-budget tracking
11. Add support bundle generator with strict redaction
12. Add customer health automation
13. Add managed support case workflow
14. Add frontend pages for Installer, Updates, SLA, and Support
15. Add tests for installer safety, update gating, rollback, SLA, support bundles, redaction, and tenant isolation

Critical safety rule:
Installer and update tooling must be dry-run/planning-first by default.
No installer output, support bundle, update plan, or rollback pack may include secrets unless explicitly requested by an admin with typed confirmation.
Real updates, real rollbacks, real restart actions, and real infrastructure mutations must require explicit confirmation and must pass readiness, safety, and backup checks.

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
- Certification engine
- Auditor portal
- Deployment pack builder
- Release attestation

If present, integrate with them.
If missing, create safe adapter interfaces.

============================================================
PHASE 25 MODULES TO ADD
============================================================

Create backend modules:

backend/app/customer_installer/
  __init__.py
  models.py
  target_profiles.py
  preflight_validator.py
  install_manifest.py
  install_plan_builder.py
  install_script_builder.py
  customer_installer_service.py

backend/app/update_channel/
  __init__.py
  models.py
  release_feed.py
  update_policy.py
  update_orchestrator.py
  rollback_manager.py
  update_service.py

backend/app/sla/
  __init__.py
  models.py
  uptime_monitor.py
  error_budget.py
  service_level_objectives.py
  sla_service.py

backend/app/support/
  __init__.py
  models.py
  support_bundle.py
  diagnostic_collector.py
  redaction.py
  support_case_service.py
  customer_health.py

backend/app/api/customer_installer.py
backend/app/api/update_channel.py
backend/app/api/sla.py
backend/app/api/support.py

Create frontend modules:

frontend/src/pages/CustomerInstaller.tsx
frontend/src/pages/ManagedUpdates.tsx
frontend/src/pages/SLA.tsx
frontend/src/pages/SupportCenter.tsx

frontend/src/components/installer/
  TargetProfileSelector.tsx
  PreflightCheckTable.tsx
  InstallPlanPanel.tsx
  InstallManifestPanel.tsx
  InstallerScriptPanel.tsx

frontend/src/components/updates/
  ReleaseChannelCard.tsx
  UpdatePolicyPanel.tsx
  UpdatePlanPanel.tsx
  RollbackPlanPanel.tsx
  ReleaseFeedTable.tsx

frontend/src/components/sla/
  SLASummaryCard.tsx
  UptimeChart.tsx
  ErrorBudgetPanel.tsx
  SLOTable.tsx
  SLAIncidentTable.tsx

frontend/src/components/support/
  SupportBundleBuilder.tsx
  DiagnosticSummary.tsx
  SupportCaseTable.tsx
  CustomerHealthScore.tsx
  RedactionPreviewPanel.tsx

frontend/src/hooks/useCustomerInstaller.ts
frontend/src/hooks/useManagedUpdates.ts
frontend/src/hooks/useSLA.ts
frontend/src/hooks/useSupport.ts

Create docs:

docs/architecture/PHASE_25_CUSTOMER_CLOUD_INSTALLER_MANAGED_UPDATES_SLA.md
docs/runbooks/CUSTOMER_INSTALLER_RUNBOOK.md
docs/runbooks/MANAGED_UPDATE_RUNBOOK.md
docs/runbooks/ROLLBACK_RUNBOOK.md
docs/runbooks/SLA_MONITORING_RUNBOOK.md
docs/runbooks/SUPPORT_BUNDLE_RUNBOOK.md

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

docs/prompt/PHASE_25_CUSTOMER_CLOUD_INSTALLER_MANAGED_UPDATE_CHANNEL_ENTERPRISE_SLA.md

The prompt file must contain this Phase 25 implementation prompt so future agents can continue from it.

============================================================
CONFIG REQUIREMENTS
============================================================

Update `.env.example`:

CUSTOMER_INSTALLER_ENABLED=true
CUSTOMER_INSTALLER_DRY_RUN=true
CUSTOMER_INSTALLER_OUTPUT_DIR=backend/data/customer_installer
CUSTOMER_INSTALLER_ALLOW_REAL_INSTALL=false
CUSTOMER_INSTALLER_REQUIRE_APPROVAL=true
CUSTOMER_INSTALLER_INCLUDE_SECRETS=false

INSTALL_TARGET_DEFAULT=docker
INSTALL_ALLOWED_TARGETS=local_vm,docker,kubernetes,cloudflare_tunnel
INSTALL_REQUIRE_PREFLIGHT_PASS=true
INSTALL_REQUIRE_BACKUP_BEFORE_MUTATION=true
INSTALL_SCRIPT_SIGNING_MODE=mock

MANAGED_UPDATES_ENABLED=true
UPDATE_CHANNEL_DEFAULT=stable
UPDATE_DRY_RUN=true
UPDATE_REQUIRE_ATTESTATION=true
UPDATE_REQUIRE_CERTIFICATION_PASS=true
UPDATE_REQUIRE_BACKUP=true
UPDATE_REQUIRE_MAINTENANCE_WINDOW=true
UPDATE_ALLOW_MAJOR_VERSION=false
UPDATE_AUTO_APPLY=false
UPDATE_ROLLBACK_ENABLED=true
UPDATE_ROLLBACK_DRY_RUN=true

RELEASE_FEED_PROVIDER=local
RELEASE_FEED_URL=
RELEASE_FEED_VERIFY_SIGNATURE=true
RELEASE_SIGNING_MODE=mock

SLA_MONITORING_ENABLED=true
SLA_DEFAULT_TIER=standard
SLA_UPTIME_TARGET_PERCENT=99.5
SLA_ERROR_BUDGET_WINDOW_DAYS=30
SLA_CHECK_INTERVAL_SECONDS=60
SLA_INCIDENT_AUTO_CREATE=true

SUPPORT_CENTER_ENABLED=true
SUPPORT_BUNDLE_ENABLED=true
SUPPORT_BUNDLE_DRY_RUN=true
SUPPORT_BUNDLE_INCLUDE_SECRETS=false
SUPPORT_BUNDLE_REQUIRE_ADMIN_APPROVAL=true
SUPPORT_BUNDLE_OUTPUT_DIR=backend/data/support_bundles
SUPPORT_REDACTION_STRICT=true

CUSTOMER_HEALTH_ENABLED=true
CUSTOMER_HEALTH_SCORE_INTERVAL_SECONDS=300

Rules:

- Installer dry-run must be true by default.
- Real install must be disabled by default.
- Managed updates must be dry-run by default.
- Auto-apply updates must be disabled by default.
- Rollback must be dry-run by default.
- Support bundles must exclude secrets by default.
- Preflight must pass before any real install or update.
- Backup must be verified before any real mutation.
- Certification and attestation should gate update plans when available.
- No secret may be logged, exposed in frontend, included in installer manifests, update plans, support bundles, or customer health exports by default.

============================================================
CUSTOMER INSTALLER MODELS
============================================================

Create Pydantic models:

1. InstallTargetType

Allowed values:
- local_vm
- docker
- kubernetes
- cloudflare_tunnel

2. InstallTargetProfile

Fields:
- id
- name
- target_type
- description
- required_tools
- required_env
- required_ports
- supported_os
- safety_notes
- created_at
- updated_at

3. PreflightCheckResult

Fields:
- id
- name
- category
- status
- severity
- message
- remediation
- metadata
- checked_at

Status:
- passed
- failed
- warning
- skipped
- manual_review_required

4. InstallManifest

Fields:
- id
- organization_id
- workspace_id
- target_type
- app_name
- release_version
- image_tags
- required_env
- required_secrets
- required_ports
- safety_defaults
- generated_files
- checksums
- generated_at

5. InstallPlan

Fields:
- id
- organization_id
- workspace_id
- target_type
- status
- dry_run
- preflight_results
- manifest
- steps
- blockers
- warnings
- requires_approval
- created_by
- created_at
- approved_by
- approved_at

6. InstallerScript

Fields:
- id
- install_plan_id
- target_type
- script_type
- content
- checksum
- signing_mode
- signature
- warnings
- generated_at

============================================================
CUSTOMER INSTALLER REQUIREMENTS
============================================================

Create:

backend/app/customer_installer/target_profiles.py

Implement built-in target profiles:

1. Local VM
- Ubuntu 24.04 recommended
- Docker optional
- systemd/NSSM notes
- minimum 8 GB RAM
- minimum 50 GB disk

2. Docker
- Docker Engine or Docker Desktop
- Docker Compose v2
- ports 80, 443, 8000, 5173 as applicable

3. Kubernetes
- kubectl
- namespace
- ingress controller
- secret management placeholder
- resource requests

4. Cloudflare Tunnel
- cloudflared
- tunnel config
- DNS readiness
- Zero Trust policy template

Create:

backend/app/customer_installer/preflight_validator.py

Validate:
- operating system metadata if available
- CPU/RAM/disk requirements if available
- required tools present if checkable
- port conflicts if checkable
- Docker Compose files present
- Kubernetes manifests present when target is kubernetes
- Cloudflare templates present when target is cloudflare_tunnel
- `.env.example` exists
- no default production secrets when APP_ENV=production
- DRY_RUN remains true by default
- Guardian risk system enabled
- social approval required
- IoT confirmation required
- auditor portal read-only if present
- deployment packs exclude secrets if present

Rules:
- Missing optional tools should be warning/manual_review_required, not crash.
- Unsafe production config must be failed severity critical.
- Results must be deterministic where possible.

Create:

backend/app/customer_installer/install_plan_builder.py

Methods:
- build_plan(target_type, context) -> InstallPlan
- approve_plan(plan_id, approved_by) -> InstallPlan
- list_plans() -> list[InstallPlan]
- get_plan(plan_id) -> InstallPlan | None

Rules:
- Plans are dry-run by default.
- Real install is blocked unless CUSTOMER_INSTALLER_ALLOW_REAL_INSTALL=true.
- Plan approval required when CUSTOMER_INSTALLER_REQUIRE_APPROVAL=true.
- Plans must include rollback and backup prerequisite steps.

Create:

backend/app/customer_installer/install_script_builder.py

Generate script templates:
- install-docker.sh
- install-local-vm.sh
- install-kubernetes.sh
- install-cloudflare-tunnel.sh

Rules:
- Scripts must be safe by default.
- Scripts must print planned actions before doing any mutation.
- Scripts must require `INSTALL_CONFIRM=yes` for real mutation.
- Scripts must not embed secrets.
- Scripts must use `.env.example` and prompt user to create `.env` securely.

============================================================
MANAGED UPDATE CHANNEL MODELS
============================================================

Create Pydantic models:

1. ReleaseChannel

Allowed values:
- dev
- beta
- stable
- enterprise_lts

2. ReleaseArtifact

Fields:
- id
- version
- channel
- git_commit
- image_tags
- changelog
- certification_run_id
- attestation_id
- checksum
- signature
- published_at
- metadata

3. UpdatePolicy

Fields:
- id
- organization_id
- workspace_id
- channel
- auto_apply
- allow_major_version
- require_certification
- require_attestation
- require_backup
- require_maintenance_window
- maintenance_window
- created_at
- updated_at

4. UpdatePlan

Fields:
- id
- organization_id
- workspace_id
- current_version
- target_version
- channel
- dry_run
- status
- steps
- blockers
- warnings
- backup_required
- rollback_plan_id
- created_by
- created_at
- approved_by
- approved_at

5. RollbackPlan

Fields:
- id
- organization_id
- workspace_id
- from_version
- to_version
- dry_run
- status
- steps
- backup_id
- validation_results
- blockers
- warnings
- created_at

============================================================
MANAGED UPDATE REQUIREMENTS
============================================================

Create:

backend/app/update_channel/release_feed.py

Implement:
- local release feed provider
- optional remote feed adapter shell
- release signature verification placeholder
- fallback to local deterministic sample releases in development

Create:

backend/app/update_channel/update_policy.py

Methods:
- get_policy(organization_id, workspace_id) -> UpdatePolicy
- update_policy(patch) -> UpdatePolicy
- evaluate_release(release, policy, context) -> dict

Rules:
- stable channel default.
- auto_apply false by default.
- major updates blocked by default.
- certification and attestation required by default when available.

Create:

backend/app/update_channel/update_orchestrator.py

Methods:
- check_for_updates(context) -> list[ReleaseArtifact]
- build_update_plan(target_version, context) -> UpdatePlan
- approve_update_plan(plan_id, approved_by) -> UpdatePlan
- apply_update(plan_id, confirmation) -> dict

Rules:
- Applying update is blocked unless UPDATE_DRY_RUN=false and confirmation == `CONFIRM_UPDATE`.
- Backup must be verified before real update.
- Maintenance window must be respected unless admin override exists.
- Certification and attestation must pass if configured.
- Never mutate infrastructure directly in Phase 25 without an explicit script/executor abstraction.
- Return planned commands, not executed destructive commands, by default.

Create:

backend/app/update_channel/rollback_manager.py

Methods:
- build_rollback_plan(from_version, to_version, context) -> RollbackPlan
- validate_rollback(plan_id) -> RollbackPlan
- execute_rollback(plan_id, confirmation) -> dict

Rules:
- Rollback is dry-run by default.
- Real rollback requires UPDATE_ROLLBACK_DRY_RUN=false and confirmation == `CONFIRM_ROLLBACK`.
- Rollback must require backup and readiness checks.
- Rollback must never delete data by default.

============================================================
SLA MODELS
============================================================

Create Pydantic models:

1. SLATier

Allowed values:
- community
- standard
- premium
- enterprise

2. ServiceLevelObjective

Fields:
- id
- organization_id
- workspace_id
- name
- target_percent
- window_days
- measurement
- enabled
- created_at
- updated_at

3. UptimeSample

Fields:
- id
- organization_id
- workspace_id
- service_name
- status
- latency_ms
- checked_at
- metadata

4. ErrorBudgetStatus

Fields:
- organization_id
- workspace_id
- slo_id
- target_percent
- actual_percent
- budget_remaining_percent
- burn_rate
- status
- calculated_at

5. SLAIncident

Fields:
- id
- organization_id
- workspace_id
- title
- severity
- status
- started_at
- resolved_at
- impact_minutes
- error_budget_impact
- linked_incident_id
- created_at
- updated_at

============================================================
SLA REQUIREMENTS
============================================================

Create:

backend/app/sla/service_level_objectives.py

Default SLOs:
- backend_api_availability 99.5%
- dashboard_availability 99.5%
- worker_queue_availability 99.0%
- scheduler_job_success 99.0%
- risk_guardian_availability 99.9%

Create:

backend/app/sla/uptime_monitor.py

Methods:
- record_sample(service_name, status, latency_ms, metadata)
- list_samples(service_name=None, limit=500)
- get_availability(service_name, window_days)

Create:

backend/app/sla/error_budget.py

Methods:
- calculate_error_budget(slo_id, context) -> ErrorBudgetStatus
- list_error_budgets(context) -> list[ErrorBudgetStatus]
- detect_burn_rate_alerts(context) -> list[dict]

Create:

backend/app/sla/sla_service.py

Methods:
- get_status(context) -> dict
- list_slos(context) -> list[ServiceLevelObjective]
- upsert_slo(request) -> ServiceLevelObjective
- record_uptime_sample(request) -> UptimeSample
- list_error_budgets(context) -> list[ErrorBudgetStatus]
- list_sla_incidents(context) -> list[SLAIncident]
- create_sla_incident(request) -> SLAIncident

Rules:
- SLA monitoring must be tenant-scoped.
- SLA incidents may link to incident command module if present.
- No external monitoring provider required in Phase 25.
- Metrics should be derived from local samples and existing health endpoints when available.

============================================================
SUPPORT CENTER MODELS
============================================================

Create Pydantic models:

1. SupportBundleRequest

Fields:
- organization_id
- workspace_id
- include_logs
- include_config
- include_metrics
- include_audit_summary
- include_certification_summary
- include_sla_summary
- include_support_cases
- include_secrets
- confirmation
- metadata

2. SupportBundle

Fields:
- id
- organization_id
- workspace_id
- status
- file_path
- size_bytes
- checksum
- redacted_fields
- warnings
- created_by
- created_at
- completed_at

3. DiagnosticSummary

Fields:
- organization_id
- workspace_id
- health_status
- risk_status
- scheduler_status
- worker_status
- update_status
- sla_status
- warnings
- generated_at

4. SupportCase

Fields:
- id
- organization_id
- workspace_id
- title
- description
- severity
- status
- owner
- tags
- linked_bundle_id
- created_by
- created_at
- updated_at
- resolved_at

5. CustomerHealthScore

Fields:
- organization_id
- workspace_id
- score
- grade
- factors
- blockers
- recommendations
- calculated_at

============================================================
SUPPORT CENTER REQUIREMENTS
============================================================

Create:

backend/app/support/redaction.py

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
- `.env` raw contents

Rules:
- Strict redaction enabled by default.
- If uncertain, redact.
- Support bundle generation must run redaction before writing files.

Create:

backend/app/support/diagnostic_collector.py

Collect:
- health endpoint summary
- config safety summary without secrets
- risk status if present
- scheduler status if present
- worker status if present
- certification summary if present
- update channel status if present
- SLA status if present
- recent event log counts
- recent error counts

Create:

backend/app/support/support_bundle.py

Methods:
- build_bundle(request, context) -> SupportBundle
- preview_bundle(request, context) -> dict
- list_bundles(context) -> list[SupportBundle]
- get_bundle(bundle_id, context) -> SupportBundle | None

Rules:
- Dry-run by default.
- Secrets excluded by default.
- include_secrets requires:
  - admin permission
  - confirmation == `CONFIRM_SUPPORT_SECRET_EXPORT`
  - SUPPORT_BUNDLE_INCLUDE_SECRETS=true
- Never include raw payment data.
- Never include private keys by default.
- Generate checksum.
- Emit audit event.

Create:

backend/app/support/customer_health.py

Score factors:
- risk guardian enabled
- dry-run safety enabled
- certification status
- SLA status
- error budget burn rate
- backup readiness
- update readiness
- unresolved critical incidents
- policy blockers
- quota or billing blockers if present

============================================================
API REQUIREMENTS
============================================================

Customer Installer API:

GET /api/customer-installer/status
GET /api/customer-installer/target-profiles
POST /api/customer-installer/preflight
POST /api/customer-installer/plans
GET /api/customer-installer/plans
GET /api/customer-installer/plans/{plan_id}
POST /api/customer-installer/plans/{plan_id}/approve
POST /api/customer-installer/plans/{plan_id}/scripts

Managed Updates API:

GET /api/updates/status
GET /api/updates/releases
GET /api/updates/policy
PATCH /api/updates/policy
POST /api/updates/check
POST /api/updates/plans
GET /api/updates/plans
GET /api/updates/plans/{plan_id}
POST /api/updates/plans/{plan_id}/approve
POST /api/updates/plans/{plan_id}/apply
POST /api/updates/rollback-plans
GET /api/updates/rollback-plans
POST /api/updates/rollback-plans/{plan_id}/validate
POST /api/updates/rollback-plans/{plan_id}/execute

SLA API:

GET /api/sla/status
GET /api/sla/slos
POST /api/sla/slos
GET /api/sla/uptime-samples
POST /api/sla/uptime-samples
GET /api/sla/error-budgets
GET /api/sla/incidents
POST /api/sla/incidents

Support API:

GET /api/support/status
POST /api/support/diagnostics
POST /api/support/bundles/preview
POST /api/support/bundles/build
GET /api/support/bundles
GET /api/support/bundles/{bundle_id}
GET /api/support/cases
POST /api/support/cases
PATCH /api/support/cases/{case_id}
GET /api/support/customer-health

All endpoints must use standard API response shape.

Required error codes:

- INSTALL_PREFLIGHT_FAILED
- INSTALL_PLAN_BLOCKED
- INSTALL_APPROVAL_REQUIRED
- INSTALL_REAL_MODE_DISABLED
- UPDATE_PLAN_BLOCKED
- UPDATE_CONFIRMATION_REQUIRED
- UPDATE_ATTESTATION_REQUIRED
- UPDATE_CERTIFICATION_REQUIRED
- ROLLBACK_BLOCKED
- ROLLBACK_CONFIRMATION_REQUIRED
- SLA_NOT_CONFIGURED
- SUPPORT_BUNDLE_BLOCKED
- SUPPORT_SECRET_EXPORT_NOT_ALLOWED
- TENANT_ACCESS_DENIED

============================================================
RBAC REQUIREMENTS
============================================================

Add permissions:

Installer:
- installer.read
- installer.plan
- installer.approve
- installer.generate_script
- installer.real_execute

Managed updates:
- updates.read
- updates.policy.manage
- updates.plan
- updates.approve
- updates.apply
- updates.rollback

SLA:
- sla.read
- sla.manage
- sla.incident.manage

Support:
- support.read
- support.case.manage
- support.bundle.preview
- support.bundle.build
- support.bundle.include_secrets

Role mapping:

admin:
- all permissions

operator:
- installer.read
- installer.plan
- installer.generate_script
- updates.read
- updates.plan
- updates.rollback
- sla.read
- sla.incident.manage
- support.read
- support.case.manage
- support.bundle.preview
- support.bundle.build

analyst:
- installer.read
- updates.read
- sla.read
- support.read
- support.bundle.preview

viewer:
- installer.read limited
- updates.read limited
- sla.read limited
- support.read limited

Rules:
- Real install, real update apply, real rollback, and support secret export are admin-only.
- Operators can build dry-run plans and bundles but cannot execute real mutations.
- All sensitive actions must be audited.

============================================================
EVENT TYPES
============================================================

Add events:

Installer:
- installer.preflight.started
- installer.preflight.completed
- installer.preflight.failed
- installer.plan.created
- installer.plan.approved
- installer.script.generated
- installer.real_mode.blocked

Updates:
- update.release_feed.loaded
- update.check.completed
- update.plan.created
- update.plan.approved
- update.apply.started
- update.apply.blocked
- update.apply.completed
- rollback.plan.created
- rollback.validated
- rollback.execute.blocked
- rollback.execute.completed

SLA:
- sla.sample.recorded
- sla.error_budget.calculated
- sla.burn_rate.warning
- sla.incident.created
- sla.incident.updated

Support:
- support.diagnostics.generated
- support.bundle.previewed
- support.bundle.started
- support.bundle.completed
- support.bundle.blocked
- support.case.created
- support.case.updated
- support.customer_health.calculated

============================================================
FRONTEND REQUIREMENTS
============================================================

Add sidebar pages:

- Customer Installer
- Managed Updates
- SLA
- Support Center

Customer Installer page must show:
- Target profile selector
- Preflight check table
- Install plan panel
- Install manifest panel
- Installer script panel
- Warnings/blockers
- Dry-run and approval status

Managed Updates page must show:
- Current version placeholder
- Release feed table
- Release channel card
- Update policy panel
- Update plan panel
- Rollback plan panel
- Certification/attestation gate status
- Backup requirement status

SLA page must show:
- SLA summary cards
- SLO table
- Uptime chart
- Error budget panel
- SLA incidents table
- Burn-rate warnings

Support Center page must show:
- Diagnostic summary
- Support bundle builder
- Redaction preview
- Support cases
- Customer health score
- Secret export blocked by default

Safety:
- Real install button hidden unless admin and enabled.
- Real update apply requires typed confirmation: CONFIRM_UPDATE.
- Real rollback requires typed confirmation: CONFIRM_ROLLBACK.
- Support secret export requires typed confirmation: CONFIRM_SUPPORT_SECRET_EXPORT.
- All update and support UI must clearly label dry-run mode.

============================================================
TEST REQUIREMENTS
============================================================

Create backend tests:

backend/app/tests/test_customer_installer_models.py
backend/app/tests/test_target_profiles.py
backend/app/tests/test_preflight_validator.py
backend/app/tests/test_install_plan_builder.py
backend/app/tests/test_install_script_builder.py
backend/app/tests/test_customer_installer_api.py

backend/app/tests/test_update_models.py
backend/app/tests/test_release_feed.py
backend/app/tests/test_update_policy.py
backend/app/tests/test_update_orchestrator.py
backend/app/tests/test_rollback_manager.py
backend/app/tests/test_update_api.py

backend/app/tests/test_sla_models.py
backend/app/tests/test_slo_service.py
backend/app/tests/test_uptime_monitor.py
backend/app/tests/test_error_budget.py
backend/app/tests/test_sla_api.py

backend/app/tests/test_support_models.py
backend/app/tests/test_support_redaction.py
backend/app/tests/test_diagnostic_collector.py
backend/app/tests/test_support_bundle.py
backend/app/tests/test_customer_health.py
backend/app/tests/test_support_api.py

backend/app/tests/test_phase25_tenant_isolation.py

Test:
- built-in installer target profiles load
- preflight catches unsafe production defaults
- preflight does not crash on missing optional tools
- install plan is dry-run by default
- real install blocked by default
- installer script contains no secrets
- release feed loads local releases
- update policy blocks major version by default
- update apply blocked without confirmation
- update apply blocked without certification/attestation when required
- rollback is dry-run by default
- rollback requires confirmation for real execution
- SLA SLOs load
- uptime samples calculate availability
- error budget burn rate works
- support redaction removes secrets
- support bundle excludes secrets by default
- support secret export requires confirmation
- customer health score calculates deterministic result
- tenant A cannot read tenant B installer/update/SLA/support data
- API endpoints return standard response shape

Create frontend tests:

frontend/src/tests/CustomerInstaller.test.tsx
frontend/src/tests/ManagedUpdates.test.tsx
frontend/src/tests/SLA.test.tsx
frontend/src/tests/SupportCenter.test.tsx

Test:
- Customer Installer page renders target profiles
- Preflight table renders
- Install script panel appears
- Managed Updates page shows release feed
- Update apply requires confirmation
- Rollback requires confirmation
- SLA page shows SLOs and error budget
- Support Center shows bundle builder
- Redaction preview appears
- Support secret export requires typed confirmation

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

- Phase 25 overview
- Customer cloud installer architecture
- Target profiles
- Preflight validator
- Install manifest and script generation
- Managed update channel
- Release feed and update policies
- Update and rollback safety gates
- SLA monitoring and error budgets
- Support bundle automation
- Customer health score
- API examples
- Frontend pages
- Test commands
- Safety checklist

Add curl examples:

Installer status:

curl http://localhost:8000/api/customer-installer/status \
  -H "Authorization: Bearer TOKEN"

Run preflight:

curl -X POST http://localhost:8000/api/customer-installer/preflight \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_type": "docker",
    "context": {}
  }'

Create install plan:

curl -X POST http://localhost:8000/api/customer-installer/plans \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_type": "docker",
    "dry_run": true
  }'

Check updates:

curl -X POST http://localhost:8000/api/updates/check \
  -H "Authorization: Bearer TOKEN"

Build update plan:

curl -X POST http://localhost:8000/api/updates/plans \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_version": "0.25.0",
    "dry_run": true
  }'

SLA status:

curl http://localhost:8000/api/sla/status \
  -H "Authorization: Bearer TOKEN"

Build support bundle preview:

curl -X POST http://localhost:8000/api/support/bundles/preview \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "include_logs": true,
    "include_config": true,
    "include_metrics": true,
    "include_secrets": false,
    "confirmation": ""
  }'

============================================================
ACCEPTANCE CRITERIA
============================================================

Phase 25 is complete only when:

- Customer installer module exists.
- Target profiles exist.
- Preflight validator works.
- Install manifest generator works.
- Install plan builder works.
- Installer script builder works and embeds no secrets.
- Managed update module exists.
- Release feed works.
- Update policy works.
- Update plan generation works.
- Update apply is blocked by default.
- Rollback plan generation works.
- Rollback execution is dry-run by default.
- SLA module exists.
- SLOs exist.
- Uptime and error budget calculations work.
- Support center module exists.
- Diagnostics collector works.
- Support bundle builder excludes secrets by default.
- Support redaction works.
- Customer health score works.
- API endpoints work.
- Frontend Customer Installer page works.
- Frontend Managed Updates page works.
- Frontend SLA page works.
- Frontend Support Center page works.
- RBAC protects sensitive actions.
- Tenant isolation is enforced.
- Event logs are emitted.
- Audit logs are created.
- Existing Phase 1–24 behavior remains intact.
- Existing tests still pass.
- New Phase 25 tests pass.
- No live trading is enabled by default.
- No real IoT action is enabled by default.
- No real social posting is enabled by default.
- No secret support bundle or installer manifest is allowed without explicit confirmation.
- README includes Phase 25 documentation.
- Prompt file exists at docs/prompt/PHASE_25_CUSTOMER_CLOUD_INSTALLER_MANAGED_UPDATE_CHANNEL_ENTERPRISE_SLA.md

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
9. docs/prompt Phase 25 prompt file
10. API examples
11. Run instructions
12. Test instructions
13. Safety checklist
14. Acceptance checklist
15. Known limitations
16. Phase 26 handoff notes

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
- Never include secrets in installer manifests by default.
- Never include secrets in update plans by default.
- Never include secrets in support bundles by default.
- Never enable live trading by default.
- Never enable real social posting by default.
- Never enable real IoT power actions by default.
- Never bypass Guardian risk checks.
- Never bypass content approval checks.
- Never bypass tenant isolation.
- Never bypass RBAC.
- Installer must be dry-run by default.
- Updates must be dry-run by default.
- Rollback must be dry-run by default.
- Support bundles must be redacted by default.
- Keep implementation modular enough for Phase 26 managed fleet control, customer agent relay, and enterprise remote diagnostics.

Now generate the complete Phase 25 implementation and save this prompt into:

docs/prompt/PHASE_25_CUSTOMER_CLOUD_INSTALLER_MANAGED_UPDATE_CHANNEL_ENTERPRISE_SLA.md
```
