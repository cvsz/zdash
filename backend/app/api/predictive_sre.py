from datetime import datetime
from fastapi import APIRouter
from app.core.responses import ok
from app.predictive_sre.anomaly_detector import AnomalyDetector
from app.predictive_sre.incident_predictor import IncidentPredictor
from app.predictive_sre.slo_forecaster import SLOForecaster
from app.predictive_sre.error_budget_service import ErrorBudgetService
from app.predictive_sre.capacity_planner import CapacityPlanner
from app.predictive_sre.reliability_advisor import ReliabilityAdvisor
from app.predictive_sre.sre_report_service import SREReportService
from app.predictive_sre.models import ForecastHorizon

router = APIRouter(prefix='/api/predictive-sre', tags=['predictive_sre'])
ctx={'organization_id':'org-demo','workspace_id':'ws-demo'}
anomaly=AnomalyDetector();incident=IncidentPredictor();slo=SLOForecaster();budget=ErrorBudgetService();capacity=CapacityPlanner();advisor=ReliabilityAdvisor();reporting=SREReportService()

@router.get('/status')
def status(): return ok({'enabled': True, 'mode': 'advisory', 'timestamp': datetime.utcnow().isoformat()})

@router.post('/anomalies/forecast')
def forecast_anomalies(): return ok(anomaly.forecast_anomalies(ctx, ForecastHorizon.one_day).model_dump())

@router.get('/anomalies')
def list_anomalies(): return ok([i.model_dump() for i in anomaly.list_forecasts()])
