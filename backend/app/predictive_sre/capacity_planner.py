from datetime import datetime
from .models import CapacityPlan,ForecastHorizon
class CapacityPlanner:
    def __init__(self): self._items=[]
    def estimate_resource_demand(self): return 74.0
    def estimate_cost_impact(self): return 180.0
    def generate_capacity_plan(self,tenant_context,resource_type,horizon:ForecastHorizon):
        d=self.estimate_resource_demand();o=CapacityPlan(id=f"cp-{len(self._items)+1}",organization_id=tenant_context["organization_id"],workspace_id=tenant_context["workspace_id"],resource_type=resource_type,current_capacity=60,forecast_demand=d,recommended_capacity=80,confidence=0.74,horizon=horizon,cost_impact_estimate=self.estimate_cost_impact(),risk_if_no_action="possible saturation",created_at=datetime.utcnow());self._items.append(o);return o
    def list_capacity_plans(self): return self._items
