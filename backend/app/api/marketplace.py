from fastapi import APIRouter, Depends
from typing import Any
from pydantic import BaseModel

from app.auth.dependencies import require_permissions
from app.auth.rbac import Permission
from app.marketplace.plugin_registry import list_plugins, get_plugin
from app.marketplace.plugin_service import (
    list_installations,
    install_plugin,
    enable_plugin,
    disable_plugin,
    uninstall_plugin,
    run_plugin_action,
)
from app.billing.entitlement_service import require_feature
from app.billing.quota_service import consume
from app.tenancy.dependencies import get_tenant_context
from app.tenancy.tenant_context import TenantContext
from app.core.responses import success_response, error_response

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])

class InstallPluginRequest(BaseModel):
    plugin_id: str
    workspace_id: str
    config: dict = {}

class RunPluginRequest(BaseModel):
    action: str
    payload: dict = {}

@router.get("/plugins")
def api_plugins(current_user: Any = Depends(require_permissions([Permission.marketplace_read]))):
    try:
        # Pydantic models need model_dump(), or we can just let FastAPI serialize it if they are ORM models.
        # list_plugins returns a list of PluginManifest models.
        plugins = [p.model_dump() if hasattr(p, "model_dump") else p for p in list_plugins()]
        return success_response({"plugins": plugins})
    except Exception as e:
        return error_response("PLUGINS_ERROR", str(e))

@router.get("/plugins/{plugin_id}")
def api_plugin(plugin_id: str, current_user: Any = Depends(require_permissions([Permission.marketplace_read]))):
    try:
        p = get_plugin(plugin_id)
        if not p:
            return error_response("PLUGIN_NOT_FOUND", "Plugin not found")
        plugin_data = p.model_dump() if hasattr(p, "model_dump") else p
        return success_response({"plugin": plugin_data})
    except Exception as e:
        return error_response("PLUGIN_ERROR", str(e))

@router.get("/installations")
def api_installations(
    current_user: Any = Depends(require_permissions([Permission.marketplace_read])),
    tenant: TenantContext = Depends(get_tenant_context)
):
    try:
        org_id = getattr(tenant, "organization_id", "default")
        ws_id: str | None = getattr(tenant, "workspace_id", None)
        insts = list_installations(org_id, ws_id)
        
        # Serialize list of installations
        res: list[dict[str, Any]] = []
        for i in insts:
            if hasattr(i, "__dict__"):
                d = dict(i.__dict__)
                d.pop('_sa_instance_state', None)
                res.append(d)
            else:
                res.append(i)  # type: ignore[arg-type]

        return success_response({"installations": res})
    except Exception as e:
        return error_response("INSTALLATIONS_ERROR", str(e))

@router.post("/install")
def api_install(
    body: InstallPluginRequest, 
    current_user: Any = Depends(require_permissions([Permission.marketplace_install])),
    _f: str = Depends(require_feature("feature.marketplace")),
    tenant: TenantContext = Depends(get_tenant_context)
):
    try:
        org_id = getattr(tenant, "organization_id", "default")
        ws_id = getattr(tenant, "workspace_id", "default")
        decision = consume(org_id, ws_id, "marketplace_plugins")
        if not decision.allowed:
            return error_response("QUOTA_EXCEEDED", "Marketplace plugins quota exceeded")
            
        res = install_plugin(
            org_id,
            body.plugin_id,
            body.workspace_id,
            body.config,
            getattr(current_user, "username", "system")
        )
        if not res.get("ok"):
            return error_response("INSTALL_FAILED", res.get("error", "Unknown error"))
        return success_response(res)
    except Exception as e:
        return error_response("INSTALL_ERROR", str(e))

@router.post("/installations/{installation_id}/enable")
def api_enable(
    installation_id: str, 
    current_user: Any = Depends(require_permissions([Permission.marketplace_manage])),
    tenant: TenantContext = Depends(get_tenant_context)
):
    try:
        org_id = getattr(tenant, "organization_id", "default")
        res = enable_plugin(org_id, installation_id, getattr(current_user, "username", "system"))
        if not res.get("ok"):
            return error_response("ENABLE_FAILED", res.get("error", "Unknown error"))
        return success_response(res)
    except Exception as e:
        return error_response("ENABLE_ERROR", str(e))

@router.post("/installations/{installation_id}/disable")
def api_disable(
    installation_id: str, 
    current_user: Any = Depends(require_permissions([Permission.marketplace_manage])),
    tenant: TenantContext = Depends(get_tenant_context)
):
    try:
        org_id = getattr(tenant, "organization_id", "default")
        res = disable_plugin(org_id, installation_id, getattr(current_user, "username", "system"))
        if not res.get("ok"):
            return error_response("DISABLE_FAILED", res.get("error", "Unknown error"))
        return success_response(res)
    except Exception as e:
        return error_response("DISABLE_ERROR", str(e))

@router.delete("/installations/{installation_id}")
def api_uninstall(
    installation_id: str, 
    current_user: Any = Depends(require_permissions([Permission.marketplace_manage])),
    tenant: TenantContext = Depends(get_tenant_context)
):
    try:
        org_id = getattr(tenant, "organization_id", "default")
        res = uninstall_plugin(org_id, installation_id, getattr(current_user, "username", "system"))
        if not res.get("ok"):
            return error_response("UNINSTALL_FAILED", res.get("error", "Unknown error"))
        return success_response(res)
    except Exception as e:
        return error_response("UNINSTALL_ERROR", str(e))

@router.post("/installations/{installation_id}/run")
def api_run(
    installation_id: str, 
    body: RunPluginRequest, 
    current_user: Any = Depends(require_permissions([Permission.marketplace_run_plugin])),
    tenant: TenantContext = Depends(get_tenant_context)
):
    try:
        org_id = getattr(tenant, "organization_id", "default")
        res = run_plugin_action(
            org_id,
            installation_id,
            body.action,
            body.payload,
            getattr(current_user, "username", "system")
        )
        if not res.get("ok"):
            return error_response("RUN_FAILED", res.get("error", "Unknown error"))
        return success_response(res)
    except Exception as e:
        return error_response("RUN_ERROR", str(e))
