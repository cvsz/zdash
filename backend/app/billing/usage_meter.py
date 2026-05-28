import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from app.db.session import SessionLocal
from app.billing.models import UsageRecord
from app.core.config import settings
from app.core.events import event_bus

logger = logging.getLogger(__name__)

def sanitize_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not metadata:
        return {}
    sanitized = {}
    for k, v in metadata.items():
        if "secret" in k.lower() or "password" in k.lower() or "token" in k.lower() or "key" in k.lower():
            sanitized[k] = "***"
        else:
            sanitized[k] = v
    return sanitized

def record_usage(
    organization_id: str, 
    workspace_id: str, 
    metric: str, 
    quantity: float = 1.0, 
    source: Optional[str] = None, 
    resource_id: Optional[str] = None, 
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    if not settings.usage_metering_enabled:
        return {"ok": True, "status": "metering_disabled"}

    try:
        clean_meta = sanitize_metadata(metadata)
        if source:
            clean_meta["source"] = source
        if resource_id:
            clean_meta["resource_id"] = resource_id

        with SessionLocal() as db:
            record = UsageRecord(
                organization_id=organization_id,
                workspace_id=workspace_id,
                metric=metric,
                quantity=quantity,
                metadata_json=clean_meta
            )
            db.add(record)
            db.commit()

        event_bus.emit(
            event_type="usage.recorded",
            source="usage_meter",
            message=f"Recorded usage for {metric}",
            payload={
                "organization_id": organization_id,
                "workspace_id": workspace_id,
                "metric": metric,
                "quantity": quantity
            }
        )

        return {"ok": True}
    except Exception as e:
        logger.error(f"Usage metering failed: {e}")
        # Failure must not crash core system
        return {"ok": False, "error": str(e)}

def get_metric_summary(organization_id: str, workspace_id: str, metric: str) -> Dict[str, Any]:
    try:
        with SessionLocal() as db:
            result = db.execute(
                select(func.sum(UsageRecord.quantity))
                .where(
                    UsageRecord.organization_id == organization_id,
                    UsageRecord.workspace_id == workspace_id,
                    UsageRecord.metric == metric
                )
            ).scalar()
            used = float(result) if result else 0.0

        return {
            "organization_id": organization_id,
            "workspace_id": workspace_id,
            "metric": metric,
            "used": used,
        }
    except Exception as e:
        logger.error(f"Failed to get metric summary: {e}")
        return {
            "organization_id": organization_id,
            "workspace_id": workspace_id,
            "metric": metric,
            "used": 0.0,
        }

def get_usage_summary(organization_id: str, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        with SessionLocal() as db:
            query = select(UsageRecord.workspace_id, UsageRecord.metric, func.sum(UsageRecord.quantity).label("total"))\
                .where(UsageRecord.organization_id == organization_id)\
                .group_by(UsageRecord.workspace_id, UsageRecord.metric)
            
            if workspace_id:
                query = query.where(UsageRecord.workspace_id == workspace_id)
                
            results = db.execute(query).all()
            
            out = []
            for row in results:
                out.append({
                    "workspace_id": row.workspace_id,
                    "metric": row.metric,
                    "used": float(row.total) if row.total else 0.0
                })
        return out
    except Exception as e:
        logger.error(f"Failed to get usage summary: {e}")
        return []

def reset_period_if_needed() -> Dict[str, Any]:
    # Placeholder for scheduled task that would reset usage or create new billing periods
    return {"ok": True, "mode": settings.usage_reset_mode}

