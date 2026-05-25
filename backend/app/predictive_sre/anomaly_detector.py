from datetime import datetime,timedelta
from .models import AnomalyForecast,ForecastHorizon,PredictionSeverity
class AnomalyDetector:
    def __init__(self): self._forecasts=[]
    def score_anomaly(self,metric_series:list[float])->float:
        if not metric_series:return 0.0
        avg=sum(metric_series)/len(metric_series)
        return min(1.0,abs(metric_series[-1]-avg)/(abs(avg)+1))
    def detect_metric_anomalies(self,tenant_context,metrics):
        return [m for m in metrics if self.score_anomaly(m.get('series',[]))>0.3]
    def forecast_anomalies(self,tenant_context,horizon:ForecastHorizon):
        now=datetime.utcnow();conf=0.72
        item=AnomalyForecast(id=f"af-{len(self._forecasts)+1}",organization_id=tenant_context['organization_id'],workspace_id=tenant_context['workspace_id'],source='observability',metric='latency_p95',severity=PredictionSeverity.warning,confidence=conf,horizon=horizon,baseline=120,forecast_value=170,anomaly_score=0.41,explanation='Rising tail latency trend',recommended_actions=['increase pool'],created_at=now,expires_at=now+timedelta(hours=6))
        self._forecasts.append(item);return item
    def list_forecasts(self): return self._forecasts
