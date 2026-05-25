from datetime import datetime, timedelta
from app.predictive_sre.models import AnomalyForecast, ForecastHorizon, PredictionSeverity

def test_anomaly_model_validation():
    item = AnomalyForecast(
        id='1', organization_id='o', workspace_id='w', source='obs', metric='latency',
        severity=PredictionSeverity.warning, confidence=0.8, horizon=ForecastHorizon.one_day,
        baseline=100, forecast_value=150, anomaly_score=0.5, explanation='rising',
        recommended_actions=['scale'], created_at=datetime.utcnow(), expires_at=datetime.utcnow()+timedelta(hours=1)
    )
    assert item.confidence == 0.8
