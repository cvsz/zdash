from typing import Optional, Dict, Any
from app.billing.entitlement_service import check_quota
from app.billing.models import EntitlementDecision
from app.billing.usage_meter import record_usage

def can_consume(organization_id: str, workspace_id: str, metric: str, quantity: float = 1.0) -> EntitlementDecision:
    return check_quota(organization_id, workspace_id, metric, quantity)

def consume(organization_id: str, workspace_id: str, metric: str, quantity: float = 1.0, source: Optional[str] = None, resource_id: Optional[str] = None) -> EntitlementDecision:
    decision = can_consume(organization_id, workspace_id, metric, quantity)
    if decision.allowed:
        record_usage(
            organization_id=organization_id,
            workspace_id=workspace_id,
            metric=metric,
            quantity=quantity,
            source=source,
            resource_id=resource_id
        )
    return decision

def get_quota_status(organization_id: str, workspace_id: Optional[str] = None) -> Dict[str, Any]:
    return {"ok": True, "status": "Quota status is currently tracked per metric."}
