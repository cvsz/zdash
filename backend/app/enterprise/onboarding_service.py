from typing import Dict, Any, Optional
from sqlalchemy import select
from app.db.session import SessionLocal
from app.enterprise.models import OnboardingChecklist
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

DEFAULT_STEPS = [
    "create organization",
    "create workspace",
    "invite team",
    "verify risk guardian",
    "run first dry-run scan",
    "run first backtest",
    "create first content item",
    "review scheduler jobs",
    "configure billing",
    "review production safety check"
]

def get_checklist(organization_id: str, workspace_id: Optional[str] = None) -> Dict[str, Any]:
    with SessionLocal() as db:
        query = select(OnboardingChecklist).where(OnboardingChecklist.organization_id == organization_id)
        if workspace_id:
            query = query.where(OnboardingChecklist.workspace_id == workspace_id)
            
        chk = db.execute(query).scalar()
        if not chk:
            chk = OnboardingChecklist(
                organization_id=organization_id,
                workspace_id=workspace_id,
                completed_steps=[],
                pending_steps=DEFAULT_STEPS,
                progress_percent=0.0
            )
            db.add(chk)
            db.commit()
            db.refresh(chk)
            
        ret = dict(chk.__dict__)
        ret.pop('_sa_instance_state', None)
        return ret

def mark_step_complete(organization_id: str, workspace_id: Optional[str], step: str) -> Dict[str, Any]:
    with SessionLocal() as db:
        query = select(OnboardingChecklist).where(OnboardingChecklist.organization_id == organization_id)
        if workspace_id:
            query = query.where(OnboardingChecklist.workspace_id == workspace_id)
            
        chk = db.execute(query).scalar()
        if not chk:
            get_checklist(organization_id, workspace_id)
            chk = db.execute(query).scalar()
        if chk is None:
            return {"ok": False, "error": "checklist not found"}
            
        if step in chk.pending_steps:
            new_pending = list(chk.pending_steps)
            new_pending.remove(step)
            chk.pending_steps = new_pending  # type: ignore[assignment]
            
            new_completed = list(chk.completed_steps)
            if step not in new_completed:
                new_completed.append(step)
            chk.completed_steps = new_completed  # type: ignore[assignment]
            
            total_steps = len(chk.completed_steps) + len(chk.pending_steps)
            chk.progress_percent = round((len(chk.completed_steps) / total_steps) * 100) if total_steps > 0 else 100.0  # type: ignore[assignment,arg-type]
            chk.updated_at = utc_now()  # type: ignore[assignment]
            db.commit()
            
    return {"ok": True}

def reset_checklist(organization_id: str, workspace_id: Optional[str] = None) -> Dict[str, Any]:
    with SessionLocal() as db:
        query = select(OnboardingChecklist).where(OnboardingChecklist.organization_id == organization_id)
        if workspace_id:
            query = query.where(OnboardingChecklist.workspace_id == workspace_id)
            
        chk = db.execute(query).scalar()
        if chk:
            chk.completed_steps = []  # type: ignore[assignment]
            chk.pending_steps = DEFAULT_STEPS  # type: ignore[assignment]
            chk.progress_percent = 0.0  # type: ignore[assignment]
            chk.updated_at = utc_now()  # type: ignore[assignment]
            db.commit()
    return {"ok": True}

def get_customer_health(organization_id: str, workspace_id: Optional[str] = None) -> Dict[str, Any]:
    chk = get_checklist(organization_id, workspace_id)
    score = chk.get("progress_percent", 0.0)
    
    status = "poor"
    if score >= 80:
        status = "excellent"
    elif score >= 50:
        status = "fair"
        
    return {
        "health_score": score,
        "status": status,
        "active_users": 1,
        "usage_trend": "stable"
    }
