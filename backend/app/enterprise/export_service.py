from typing import Dict, Any, List, Optional
from sqlalchemy import select
from app.db.session import SessionLocal
from app.enterprise.models import ExportBundle, ExportStatus
from datetime import datetime, timezone
import os

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def create_export_bundle(request: Dict[str, Any]) -> Dict[str, Any]:
    with SessionLocal() as db:
        bundle = ExportBundle(
            organization_id=request["organization_id"],
            workspace_id=request.get("workspace_id"),
            export_type=request.get("export_type", "full"),
            status=ExportStatus.pending,
            include_audit_logs=request.get("include_audit_logs", False),
            include_content=request.get("include_content", True),
            include_backtests=request.get("include_backtests", False),
            include_scheduler=request.get("include_scheduler", True),
            include_secrets=request.get("include_secrets", False),
            created_by="system" # should come from request ideally
        )
        db.add(bundle)
        db.commit()
        db.refresh(bundle)
        
        # Async generation placeholder
        bundle.status = ExportStatus.completed
        bundle.file_path = f"/tmp/exports/{bundle.id}.zip"
        bundle.completed_at = utc_now()
        db.commit()
        db.refresh(bundle)
        
        ret = dict(bundle.__dict__)
        ret.pop('_sa_instance_state', None)
        return {"ok": True, "bundle": ret}

def get_export_bundle(organization_id: str, bundle_id: str) -> Dict[str, Any]:
    with SessionLocal() as db:
        bundle = db.execute(select(ExportBundle).where(ExportBundle.id == bundle_id).where(ExportBundle.organization_id == organization_id)).scalar()
        if not bundle:
            return {"ok": False, "error": "NOT_FOUND"}
            
        ret = dict(bundle.__dict__)
        ret.pop('_sa_instance_state', None)
        return {"ok": True, "bundle": ret}

def list_export_bundles(organization_id: str) -> List[Dict[str, Any]]:
    with SessionLocal() as db:
        bundles = db.execute(select(ExportBundle).where(ExportBundle.organization_id == organization_id).order_by(ExportBundle.created_at.desc())).scalars().all()
        res = []
        for b in bundles:
            d = dict(b.__dict__)
            d.pop('_sa_instance_state', None)
            res.append(d)
        return res

def import_bundle(file_path: str) -> Dict[str, Any]:
    return {"ok": True, "status": "imported"}
