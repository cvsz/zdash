from __future__ import annotations
from .health_analyzer import HealthAnalyzer


class OpsAutopilot:
    def __init__(self, health_analyzer: HealthAnalyzer):
        self.health_analyzer = health_analyzer

    def evaluate_system(self, organization_id: str, workspace_id: str):
        snap = self.health_analyzer.collect_snapshot(organization_id, workspace_id)
        return {
            "snapshot": snap.model_dump(),
            "recommendations": [],
            "mode": "advisory",
            "dry_run": True,
        }

    def create_incidents_from_health(self, snapshot):
        return []

    def propose_remediations(self, incident_id: str):
        return []

    def run_approved_remediations(self, incident_id: str):
        return []

    def get_autopilot_status(self):
        return {"mode": "advisory", "dry_run": True, "require_approval": True}
