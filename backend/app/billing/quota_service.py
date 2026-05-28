import logging
from typing import Optional, Dict, Any
from app.billing.entitlement_service import check_quota
from app.billing.models import EntitlementDecision
from app.billing.usage_meter import record_usage
from app.core.config import settings
from app.core.events import event_bus

logger = logging.getLogger(__name__)

def can_consume(organization_id: str, workspace_id: str, metric: str, quantity: float = 1.0) -> EntitlementDecision:
    decision = check_quota(organization_id, workspace_id, metric, quantity)
    
    if not settings.usage_enforcement_enabled:
        decision.allowed = True
        decision.reason = "enforcement_disabled"
        return decision

    if not decision.allowed:
        decision.reason = "QUOTA_EXCEEDED"
        
    return decision

def consume(
    organization_id: str, 
    workspace_id: str, 
    metric: str, 
    quantity: float = 1.0, 
    source: Optional[str] = None, 
    resource_id: Optional[str] = None
) -> EntitlementDecision:
    
    decision = can_consume(organization_id, workspace_id, metric, quantity)
    
    if not decision.allowed:
        # Emit exceeded event
        event_bus.emit(
            event_type="usage.quota.exceeded",
            source="quota_service",
            message=f"Quota exceeded for {metric}",
            payload={
                "organization_id": organization_id,
                "workspace_id": workspace_id,
                "metric": metric,
                "quantity": quantity,
                "quota": decision.quota,
                "usage": decision.usage
            }
        )
        logger.warning(f"Quota exceeded: org={organization_id} ws={workspace_id} metric={metric}")
        return decision
        
    # We are allowed to consume. Record it.
    record_usage(
        organization_id=organization_id,
        workspace_id=workspace_id,
        metric=metric,
        quantity=quantity,
        source=source,
        resource_id=resource_id
    )
    
    # Check warning threshold
    if decision.quota is not None and decision.quota > 0:
        new_usage = (decision.usage or 0) + quantity
        threshold = decision.quota * 0.8
        if new_usage > threshold and (decision.usage or 0) <= threshold:
            # Emit warning only once when crossing the 80% threshold
            event_bus.emit(
                event_type="usage.quota.warning",
                source="quota_service",
                message=f"Quota warning for {metric}: >80% used",
                payload={
                    "organization_id": organization_id,
                    "workspace_id": workspace_id,
                    "metric": metric,
                    "quota": decision.quota,
                    "usage": new_usage
                }
            )
            logger.info(f"Quota warning: org={organization_id} ws={workspace_id} metric={metric} at {new_usage}/{decision.quota}")

    return decision

def get_quota_status(organization_id: str, workspace_id: Optional[str] = None) -> Dict[str, Any]:
    return {"ok": True, "status": "Quota status is currently tracked per metric."}
