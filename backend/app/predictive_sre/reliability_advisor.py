from datetime import datetime
from .models import ReliabilityRecommendation, PredictionSeverity, PredictionStatus


class ReliabilityAdvisor:
    def __init__(self):
        self._items = []

    def generate_recommendations(self, tenant_context):
        r = ReliabilityRecommendation(
            id=f"rr-{len(self._items) + 1}",
            organization_id=tenant_context["organization_id"],
            workspace_id=tenant_context["workspace_id"],
            title="Tune autoscaling bounds",
            category="capacity",
            severity=PredictionSeverity.warning,
            confidence=0.7,
            rationale="Demand forecast exceeds headroom",
            actions=["raise min replicas after approval"],
            safety_impact="safe advisory",
            cost_impact="moderate",
            status=PredictionStatus.generated,
            created_at=datetime.utcnow(),
        )
        self._items.append(r)
        return [r]

    def prioritize_recommendations(self):
        return sorted(
            self._items, key=lambda i: (i.severity.value, i.confidence), reverse=True
        )

    def explain_recommendation(self):
        return "Recommendation is estimate; requires approval."

    def list_recommendations(self):
        return self._items
