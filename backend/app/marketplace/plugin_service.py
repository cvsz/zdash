from typing import Dict, Any, List
from datetime import datetime, timezone
from app.db.session import SessionLocal
from app.marketplace.models import PluginInstallation, PluginInstallStatus
from app.marketplace.plugin_runtime import run_action
from app.marketplace.safety import check_plugin_action
from app.billing.entitlement_service import check_feature
from app.billing.quota_service import consume
from app.core.events import event_bus
from app.audit.audit_service import AuditService
from app.audit.models import AuditLogCreate
from app.db.repositories import MarketplaceRepository


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def list_installations(organization_id: str, workspace_id: str = None) -> List[PluginInstallation]:
    with SessionLocal() as db:
        repo = MarketplaceRepository(db)
        return repo.list_installations(organization_id, workspace_id)

def install_plugin(organization_id: str, plugin_id: str, workspace_id: str, config: dict = None, installed_by: str = "system") -> Dict[str, Any]:
    ent = check_feature(organization_id, "feature.marketplace")
    if not ent.allowed:
        return {"ok": False, "error": "FEATURE_NOT_ENTITLED"}

    quota = consume(organization_id, workspace_id, "marketplace_plugins")
    if not quota.allowed:
        return {"ok": False, "error": "QUOTA_EXCEEDED"}

    with SessionLocal() as db:
        repo = MarketplaceRepository(db)
        audit = AuditService(db)

        inst = repo.create_installation(
            organization_id=organization_id,
            workspace_id=workspace_id,
            plugin_id=plugin_id,
            version="1.0.0",
            status=PluginInstallStatus.installed,
            config_json=config or {},
            enabled=False,
            installed_by=installed_by
        )
        
        event_bus.emit(
            "marketplace.plugin.installed",
            "plugin_service",
            f"Plugin {plugin_id} installed",
            {"plugin_id": plugin_id, "installation_id": inst.id, "organization_id": organization_id, "workspace_id": workspace_id}
        )
        
        audit.log(AuditLogCreate(
            actor_user_id=installed_by,
            actor_email="",
            action="install_plugin",
            resource_type="plugin_installation",
            resource_id=inst.id,
            result="success"
        ))

        ret = dict(inst.__dict__)
        ret.pop('_sa_instance_state', None)
        ret["ok"] = True
        return ret

def enable_plugin(organization_id: str, installation_id: str, actor_id: str = "system") -> Dict[str, Any]:
    with SessionLocal() as db:
        repo = MarketplaceRepository(db)
        audit = AuditService(db)
        inst = repo.get_installation(organization_id, installation_id)
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}
            
        inst.enabled = True
        inst.status = PluginInstallStatus.enabled
        inst.updated_at = utc_now()
        repo.update_installation(inst)
        
        event_bus.emit("marketplace.plugin.enabled", "plugin_service", f"Plugin {inst.plugin_id} enabled", {"installation_id": installation_id, "organization_id": organization_id})
        audit.log(AuditLogCreate(actor_user_id=actor_id, actor_email="", action="enable_plugin", resource_type="plugin_installation", resource_id=installation_id, result="success"))

    return {"ok": True}

def disable_plugin(organization_id: str, installation_id: str, actor_id: str = "system") -> Dict[str, Any]:
    with SessionLocal() as db:
        repo = MarketplaceRepository(db)
        audit = AuditService(db)
        inst = repo.get_installation(organization_id, installation_id)
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}
            
        inst.enabled = False
        inst.status = PluginInstallStatus.disabled
        inst.updated_at = utc_now()
        repo.update_installation(inst)
        
        event_bus.emit("marketplace.plugin.disabled", "plugin_service", f"Plugin {inst.plugin_id} disabled", {"installation_id": installation_id, "organization_id": organization_id})
        audit.log(AuditLogCreate(actor_user_id=actor_id, actor_email="", action="disable_plugin", resource_type="plugin_installation", resource_id=installation_id, result="success"))

    return {"ok": True}

def uninstall_plugin(organization_id: str, installation_id: str, actor_id: str = "system") -> Dict[str, Any]:
    with SessionLocal() as db:
        repo = MarketplaceRepository(db)
        audit = AuditService(db)
        inst = repo.get_installation(organization_id, installation_id)
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}
            
        plugin_id = inst.plugin_id
        repo.delete_installation(inst)
        
        event_bus.emit("marketplace.plugin.uninstalled", "plugin_service", f"Plugin {plugin_id} uninstalled", {"installation_id": installation_id, "organization_id": organization_id})
        audit.log(AuditLogCreate(actor_user_id=actor_id, actor_email="", action="uninstall_plugin", resource_type="plugin_installation", resource_id=installation_id, result="success"))

    return {"ok": True}

def run_plugin_action(organization_id: str, installation_id: str, action: str, payload: dict, actor_id: str = "system") -> Dict[str, Any]:
    with SessionLocal() as db:
        repo = MarketplaceRepository(db)
        audit = AuditService(db)
        inst = repo.get_installation(organization_id, installation_id)
        if not inst:
            return {"ok": False, "error": "INSTALLATION_NOT_FOUND"}
            
        if not inst.enabled:
            return {"ok": False, "error": "PLUGIN_DISABLED"}
            
        plugin_id = inst.plugin_id
        
        event_bus.emit("marketplace.plugin.action.started", "plugin_service", f"Running {action} on {plugin_id}", {"installation_id": installation_id, "action": action})

        ok, msg = check_plugin_action(action, payload)
        if not ok:
            event_bus.emit("marketplace.plugin.action.blocked", "plugin_service", f"Action {action} blocked: {msg}", {"installation_id": installation_id, "action": action, "reason": msg})
            audit.log(AuditLogCreate(actor_user_id=actor_id, actor_email="", action="run_plugin_action", resource_type="plugin_installation", resource_id=installation_id, result="blocked", metadata={"reason": msg}))
            return {"ok": False, "error": msg}
            
        result = run_action(plugin_id, action, payload)
        
        event_bus.emit("marketplace.plugin.action.completed", "plugin_service", f"Action {action} completed on {plugin_id}", {"installation_id": installation_id, "action": action})
        audit.log(AuditLogCreate(actor_user_id=actor_id, actor_email="", action="run_plugin_action", resource_type="plugin_installation", resource_id=installation_id, result="success", metadata={"action": action}))

        return result
