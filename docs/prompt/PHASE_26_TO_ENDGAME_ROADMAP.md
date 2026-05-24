# zDash · Phase 26 → Endgame Roadmap

Repository target: `cvsz/zdash`

This roadmap continues after:

- Phase 23 · Sovereign Enterprise Control Plane
- Phase 24 · Autonomous Certification + External Auditor Portal + Enterprise Customer Deployment Packs
- Phase 25 · Customer Cloud Installer + Managed Update Channel + Enterprise SLA Automation

Use each prompt file one phase at a time. Every phase must inspect the repository first, preserve existing behavior, create compatibility shims for missing intermediate modules, and keep all safety defaults locked.

## Phase 26 · Managed Fleet Control + Customer Agent Relay + Remote Diagnostics

Target prompt file:

`docs/prompt/PHASE_26_MANAGED_FLEET_CONTROL_CUSTOMER_AGENT_RELAY_REMOTE_DIAGNOSTICS.md`

Goal: manage many customer zDash installations from a tenant-safe fleet control plane, with customer-side agent relay, heartbeat, diagnostics, update visibility, support access approval, and remote command planning. Remote actions must be approval-gated and dry-run by default.

## Phase 27 · Autonomous Remediation + Change Advisory Board + Safe Execution

Target prompt file:

`docs/prompt/PHASE_27_AUTONOMOUS_REMEDIATION_CHANGE_ADVISORY_SAFE_EXECUTION.md`

Goal: add AI-assisted remediation proposals, change advisory workflows, blast-radius analysis, rollback-first execution plans, approval gates, and safe command execution adapters. The system may recommend remediation, but real execution is blocked unless explicitly approved.

## Phase 28 · Partner Marketplace SDK + Plugin Certification + Developer Portal

Target prompt file:

`docs/prompt/PHASE_28_PARTNER_MARKETPLACE_SDK_PLUGIN_CERTIFICATION_DEVELOPER_PORTAL.md`

Goal: turn the marketplace into a governed partner ecosystem with plugin SDK, sandbox tests, certification, revenue-share placeholders, developer portal, documentation generation, and signed plugin manifests. Plugins remain sandboxed by default.

## Phase 29 · Global Data Residency + Regional Control Plane + Compliance Automation

Target prompt file:

`docs/prompt/PHASE_29_GLOBAL_DATA_RESIDENCY_REGIONAL_CONTROL_PLANE_COMPLIANCE_AUTOMATION.md`

Goal: add regional tenant placement, data residency policy enforcement, regional backup topology, cross-region DR planning, compliance mapping, and export boundaries. Cross-region data movement must be denied unless policy permits it.

## Phase 30 · Enterprise AI SOC + Threat Intelligence + Abuse Detection

Target prompt file:

`docs/prompt/PHASE_30_ENTERPRISE_AI_SOC_THREAT_INTELLIGENCE_ABUSE_DETECTION.md`

Goal: add an AI security operations center layer with anomaly detection, auth abuse detection, plugin risk signals, suspicious automation detection, IOC ingestion stubs, alert correlation, and incident enrichment. It must not perform intrusive scanning or unsafe offensive actions.

## Phase 31 · Sovereign Offline Edition + Air-Gapped Deployment + License Ops

Target prompt file:

`docs/prompt/PHASE_31_SOVEREIGN_OFFLINE_AIRGAPPED_DEPLOYMENT_LICENSE_OPS.md`

Goal: package zDash for offline/air-gapped customers with offline license verification, offline update bundles, offline audit exports, offline docs, offline seed data, and customer handoff. No external network dependency should be required in offline mode.

## Phase 32 · ENDGAME · GA Release Orchestrator + Enterprise Operating System Pack

Target prompt file:

`docs/prompt/PHASE_32_ENDGAME_GA_RELEASE_ORCHESTRATOR_ENTERPRISE_OS_PACK.md`

Goal: final endgame release layer that assembles all modules into a GA-ready enterprise operating system pack: release checklist, golden path installer, final docs index, go-live evidence, customer runbooks, CI quality gates, launch readiness, and long-term maintenance plan.

## Global rules for every remaining phase

- Never enable live trading by default.
- Never enable real IoT actions by default.
- Never enable real social posting by default.
- Never expose or export secrets by default.
- Never bypass Guardian risk checks.
- Never bypass content approval checks.
- Never bypass tenant isolation.
- Never bypass RBAC.
- Dry-run/planning mode must be the default for all customer-impacting operations.
- Real execution requires admin permission, typed confirmation, passing preflight checks, backup readiness, and audit logging.
- Existing backend and frontend tests must continue to pass.
- New tests must be added for every new module.
