from datetime import datetime,timedelta
from .models import ErrorBudgetForecast
class ErrorBudgetService:
    def __init__(self): self._items=[]
    def calculate_current_burn(self): return 1.2
    def forecast_burn(self,tenant_context,slo_name="availability"):
        o=ErrorBudgetForecast(id=f"eb-{len(self._items)+1}",organization_id=tenant_context["organization_id"],workspace_id=tenant_context["workspace_id"],slo_name=slo_name,current_burn_rate=1.2,forecast_burn_rate=1.6,remaining_budget_percent=48.0,exhaustion_eta=datetime.utcnow()+timedelta(days=5),confidence=0.69,recommended_actions=["throttle background jobs"],created_at=datetime.utcnow());self._items.append(o);return o
    def list_error_budget_forecasts(self): return self._items
    def generate_error_budget_report(self): return {"count":len(self._items)}
