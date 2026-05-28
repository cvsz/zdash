from datetime import UTC, datetime, timedelta

from app.predictive_sre.models import (
    AnomalyForecast,
    ForecastHorizon,
    PredictionSeverity,
)


def test_anomaly_model_validation():
    created_at = datetime.now(UTC)
    item = AnomalyForecast(
        id="1",
        organization_id="o",
        workspace_id="w",
        source="obs",
        metric="latency",
        severity=PredictionSeverity.warning,
        confidence=0.8,
        horizon=ForecastHorizon.one_day,
        baseline=100,
        forecast_value=150,
        anomaly_score=0.5,
        explanation="rising",
        recommended_actions=["scale"],
        created_at=created_at,
        expires_at=created_at + timedelta(hours=1),
    )
    assert item.confidence == 0.8
