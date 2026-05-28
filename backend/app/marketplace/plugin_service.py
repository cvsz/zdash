from typing import Dict, Any, List
from sqlalchemy import select
from app.db.session import SessionLocal
from app.marketplace.models import PluginInstallation, PluginInstallStatus
from app.marketplace.plugin_runtime import run_action
from app.marketplace.safety import check_plugin_action
from app.billing.entitlement_service import check_feature
from app.billing.quota_service import consume
from datetime import datetime, timezone
import uuid

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def list_installations(organization_id: str, workspace_id: str = None) -> List[PluginInstallation]:
    with SessionLocal() as db:
        query = select(PluginInstallation).where(PluginInstallation.organization_id == organization_id)
        if workspace_id:
            query = query.where(PluginInstallation.workspace_id == workspace_id)
        return db.execute(query).scalars().all()

def install_plugin(organization_id: str, plugin_id: str, workspace_id: str, config: dict = None, installed_by: str = "system") -> Dict[str, Any]:
    # Check entitlement
    ent = check_feature(organization_id, "feature.marketplace")
    if not ent.allowed:
        return {"ok": False, "error": "FEATURE_NOT_ENTITLED"}

    # Check quota
    quota = consume(organization_id, workspace_id, "marketplace_plugins")
    if not quota.allowed:
        return {"ok": False, "error": "QUOTA_EXCEEDED"}

    with SessionLocal() as db:
        inst = PluginInstallation(
            organization_id=organization_id,
            workspace_id=workspace_id,
            plugin_id=plugin_id,
            version="1.0.0",
            status=PluginInstallStatus.installed,
            config_json=config or {},
            enabled=False,
            installed_by=installed_by
        )
        db.add(inst)
        db.commit()
        db.refresh(inst)
        
        # remove internal state before return or return dict
        ret = dict(inst.__dict__)
        ret.pop('_sa_instance_state', None)
        ret["ok"] = True
        return ret

def enable_plugin(organization_id: str, installation_id: str) -> Dict[str, Any]:
    with SessionLocal() as db:
        inst = db.execute(select(PluginInstallation).where(PluginInstallation.id == installation_id).where(PluginInstallation.organization_id == organization_id)).scalar()
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}
            
        inst.enabled = True
        inst.status = PluginInstallStatus.enabled
        inst.updated_at = utc_now()
        db.commit()
    return {"ok": True}

def disable_plugin(organization_id: str, installation_id: str) -> Dict[str, Any]:
    with SessionLocal() as db:
        inst = db.execute(select(PluginInstallation).where(PluginInstallation.id == installation_id).where(PluginInstallation.organization_id == organization_id)).scalar()
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}
            
        inst.enabled = False
        inst.status = PluginInstallStatus.disabled
        inst.updated_at = utc_now()
        db.commit()
    return {"ok": True}

def uninstall_plugin(organization_id: str, installation_id: str) -> Dict[str, Any]:
    with SessionLocal() as db:
        inst = db.execute(select(PluginInstallation).where(PluginInstallation.id == installation_id).where(PluginInstallation.organization_id == organization_id)).scalar()
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}
            
        db.delete(inst)
        db.commit()
    return {"ok": True}

def run_plugin_action(organization_id: str, installation_id: str, action: str, payload: dict) -> Dict[str, Any]:
    with SessionLocal() as db:
        inst = db.execute(select(PluginInstallation).where(PluginInstallation.id == installation_id).where(PluginInstallation.organization_id == organization_id)).scalar()
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}
            
        if not inst.enabled:
            return {"ok": False, "error": "PLUGIN_DISABLED"}
            
        ok, msg = check_plugin_action(action, payload)
        if not ok:
            return {"ok": False, "error": msg}
            
        return run_action(inst.plugin_id, action, payload)
