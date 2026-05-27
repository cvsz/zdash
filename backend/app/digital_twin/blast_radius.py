from .models import BlastRadiusResult


class BlastRadiusService:
    def __init__(self, graph):
        self.graph = graph
        self._results = []

    def recommend_mitigations(self, severity):
        return (
            ["increase monitoring", "prepare rollback"]
            if severity != "low"
            else ["monitor"]
        )

    def analyze_blast_radius(self, org, ws, target_entity_id, severity):
        neighbors = self.graph.get_neighbors(org, ws, target_entity_id)
        result = BlastRadiusResult(
            id=f"br-{len(self._results) + 1}",
            organization_id=org,
            workspace_id=ws,
            target_entity_id=target_entity_id,
            severity=severity,
            affected_domains=["operations", "revenue"],
            affected_entities=[{"relationship_id": r.id} for r in neighbors],
            mitigation_options=self.recommend_mitigations(severity),
            confidence=0.55,
            limitations=["advisory only"],
        )
        self._results.append(result)
        return result

    def list_blast_radius_results(self, org, ws):
        return [
            r
            for r in self._results
            if r.organization_id == org and r.workspace_id == ws
        ]
