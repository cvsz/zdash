from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from app.db.session import SessionLocal
from app.billing.models import UsageRecord

def record_usage(organization_id: str, workspace_id: str, metric: str, quantity: float = 1.0, **kwargs) -> Dict[str, Any]:
    with SessionLocal() as db:
        record = UsageRecord(
            organization_id=organization_id,
            workspace_id=workspace_id,
            metric=metric,
            quantity=quantity,
            metadata_json=kwargs
        )
        db.add(record)
        db.commit()
    return {"ok": True}

def get_metric_summary(organization_id: str, workspace_id: str, metric: str) -> Dict[str, Any]:
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

def get_usage_summary(organization_id: str, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
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

def reset_period_if_needed() -> Dict[str, Any]:
    return {"ok": True}
