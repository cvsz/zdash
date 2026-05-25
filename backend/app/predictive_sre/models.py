from __future__ import annotations
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator

class PredictionStatus(str, Enum):
    generated='generated'; warning='warning'; low_confidence='low_confidence'; blocked='blocked'; expired='expired'
class PredictionSeverity(str, Enum):
    info='info'; warning='warning'; critical='critical'; emergency='emergency'
class ForecastHorizon(str, Enum):
    one_hour='one_hour'; six_hours='six_hours'; one_day='one_day'; seven_days='seven_days'; thirty_days='thirty_days'
class _Base(BaseModel):
    id:str; organization_id:str; workspace_id:str
class AnomalyForecast(_Base):
    source:str; metric:str; severity:PredictionSeverity; confidence:float=Field(ge=0,le=1); horizon:ForecastHorizon; baseline:float; forecast_value:float; anomaly_score:float; explanation:str; recommended_actions:list[str]=[]; created_at:datetime; expires_at:datetime
class IncidentPrediction(_Base):
    predicted_incident_type:str; severity:PredictionSeverity; confidence:float=Field(ge=0,le=1); horizon:ForecastHorizon; affected_services:list[str]=[]; likely_causes:list[str]=[]; recommended_prevention:list[str]=[]; evidence:list[str]=[]; status:PredictionStatus; created_at:datetime; expires_at:datetime
class SLOForecast(_Base):
    slo_name:str; current_value:float; forecast_value:float; target_value:float; breach_probability:float=Field(ge=0,le=1); confidence:float=Field(ge=0,le=1); horizon:ForecastHorizon; explanation:str; created_at:datetime
class ErrorBudgetForecast(_Base):
    slo_name:str; current_burn_rate:float; forecast_burn_rate:float; remaining_budget_percent:float; exhaustion_eta:datetime|None=None; confidence:float=Field(ge=0,le=1); recommended_actions:list[str]=[]; created_at:datetime
class CapacityPlan(_Base):
    resource_type:str; current_capacity:float; forecast_demand:float; recommended_capacity:float; confidence:float=Field(ge=0,le=1); horizon:ForecastHorizon; cost_impact_estimate:float; risk_if_no_action:str; created_at:datetime
class ReliabilityRecommendation(_Base):
    title:str; category:str; severity:PredictionSeverity; confidence:float=Field(ge=0,le=1); rationale:str; actions:list[str]=[]; safety_impact:str; cost_impact:str; status:PredictionStatus; created_at:datetime
