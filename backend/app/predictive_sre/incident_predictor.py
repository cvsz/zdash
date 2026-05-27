from datetime import datetime, timedelta
from .models import (
    IncidentPrediction,
    ForecastHorizon,
    PredictionSeverity,
    PredictionStatus,
)


class IncidentPredictor:
    def __init__(self):
        self._items = []

    def score_incident_risk(self, signals):
        return min(1.0, 0.4 + 0.1 * len(signals))

    def predict_incidents(self, tenant_context, horizon: ForecastHorizon):
        c = self.score_incident_risk(["latency"])
        p = IncidentPrediction(
            id=f"ip-{len(self._items) + 1}",
            organization_id=tenant_context["organization_id"],
            workspace_id=tenant_context["workspace_id"],
            predicted_incident_type="latency_degradation",
            severity=PredictionSeverity.warning,
            confidence=c,
            horizon=horizon,
            affected_services=["api"],
            likely_causes=["capacity pressure"],
            recommended_prevention=["scale replicas (approval required)"],
            evidence=["p95 latency up 22%"],
            status=PredictionStatus.generated,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=6),
        )
        self._items.append(p)
        return p

    def list_predictions(self):
        return self._items

    def convert_prediction_to_incident(self, prediction_id, has_permission=False):
        if not has_permission:
            raise PermissionError("convert permission required")
        return {"incident_id": f"inc-{prediction_id}", "status": "created"}
