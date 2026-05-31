from fastapi import APIRouter, Depends
from typing import Any
from pydantic import BaseModel
from sqlalchemy import select

from app.auth.dependencies import require_permissions
from app.auth.models import AuthSession
from app.auth.rbac import Permission
from app.db.session import SessionLocal
from app.marketplace.models import (
    PluginManifest,
    PluginStatus,
    installation_to_dict,
    manifest_to_dict,
)
from app.marketplace.plugin_registry import (
    list_plugins,
    get_plugin,
    register_plugin_manifest,
    validate_plugin_manifest,
)
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


def _serialize_plugin(plugin: Any) -> dict[str, Any]:
    if isinstance(plugin, dict):
        return plugin
    if isinstance(plugin, PluginManifest):
        return manifest_to_dict(plugin)
    if hasattr(plugin, "model_dump"):
        return plugin.model_dump()
    if hasattr(plugin, "__dict__"):
        data = dict(plugin.__dict__)
        data.pop("_sa_instance_state", None)
        return data
    return {"id": str(plugin)}


class InstallPluginRequest(BaseModel):
    plugin_id: str
    workspace_id: str
    config: dict = {}


class RunPluginRequest(BaseModel):
    action: str
    payload: dict = {}


class RegisterManifestRequest(BaseModel):
    name: str
    slug: str
    version: str = "1.0.0"
    description: str = ""
    author: str = "zDash"
    category: str = "general"
    status: str = PluginStatus.draft.value
    required_features: list[str] = []
    required_permissions: list[str] = []
    config_schema: dict = {}
    default_config: dict = {}
    entrypoint: str = ""
    safety_level: str = "sandbox"
    metadata: dict = {}


@router.get("/categories")
def api_categories(
    current_user: Any = Depends(require_permissions([Permission.marketplace_read])),
):
    try:
        with SessionLocal() as db:
            rows = (
                db.execute(
                    select(PluginManifest.category)
                    .distinct()
                    .order_by(PluginManifest.category)
                )
                .scalars()
                .all()
            )
        categories = (
            list(rows)
            if rows
            else [
                "general",
                "risk",
                "backtesting",
                "content",
                "automation",
                "data",
                "analytics",
                "ai",
            ]
        )
        return success_response({"categories": categories})
    except Exception as e:
        return error_response("CATEGORIES_ERROR", str(e))


@router.get("/plugins")
def api_plugins(
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
    current_user: Any = Depends(require_permissions([Permission.marketplace_read])),
):
    try:
        plugins = list_plugins(search=search, category=category, status=status)
        return success_response({"plugins": plugins})
    except Exception as e:
        return error_response("PLUGINS_ERROR", str(e))


@router.get("/plugins/{plugin_id}")
def api_plugin(
    plugin_id: str,
    current_user: Any = Depends(require_permissions([Permission.marketplace_read])),
):
    try:
        plugin = get_plugin(plugin_id=plugin_id)
        if not plugin:
            return error_response("PLUGIN_NOT_FOUND", "Plugin not found")
        plugin_data = (
            manifest_to_dict(plugin) if isinstance(plugin, PluginManifest) else plugin
        )
        return success_response({"plugin": plugin_data})
    except Exception as e:
        return error_response("PLUGIN_ERROR", str(e))


@router.get("/installations")
def api_installations(
    current_user: Any = Depends(require_permissions([Permission.marketplace_read])),
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        org_id = getattr(tenant, "organization_id", "default")
        ws_id: str | None = getattr(tenant, "workspace_id", None)
        insts = list_installations(org_id, ws_id)

        res = [installation_to_dict(inst) for inst in insts]
        return success_response({"installations": res})
    except Exception as e:
        return error_response("INSTALLATIONS_ERROR", str(e))


@router.post("/install")
def api_install(
    body: InstallPluginRequest,
    current_user: Any = Depends(require_permissions([Permission.marketplace_install])),
    _f: str = Depends(require_feature("feature.marketplace")),
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        org_id = getattr(tenant, "organization_id", "default")
        decision = consume(
            org_id, getattr(tenant, "workspace_id", "default"), "marketplace_plugins"
        )
        if not decision.allowed:
            return error_response(
                "QUOTA_EXCEEDED", "Marketplace plugins quota exceeded"
            )

        res = install_plugin(
            org_id,
            body.plugin_id,
            body.workspace_id,
            body.config,
            getattr(current_user, "username", "system"),
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
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        org_id = getattr(tenant, "organization_id", "default")
        res = enable_plugin(
            org_id, installation_id, getattr(current_user, "username", "system")
        )
        if not res.get("ok"):
            return error_response("ENABLE_FAILED", res.get("error", "Unknown error"))
        return success_response(res)
    except Exception as e:
        return error_response("ENABLE_ERROR", str(e))


@router.post("/installations/{installation_id}/disable")
def api_disable(
    installation_id: str,
    current_user: Any = Depends(require_permissions([Permission.marketplace_manage])),
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        org_id = getattr(tenant, "organization_id", "default")
        res = disable_plugin(
            org_id, installation_id, getattr(current_user, "username", "system")
        )
        if not res.get("ok"):
            return error_response("DISABLE_FAILED", res.get("error", "Unknown error"))
        return success_response(res)
    except Exception as e:
        return error_response("DISABLE_ERROR", str(e))


@router.delete("/installations/{installation_id}")
def api_uninstall(
    installation_id: str,
    current_user: Any = Depends(require_permissions([Permission.marketplace_manage])),
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        org_id = getattr(tenant, "organization_id", "default")
        res = uninstall_plugin(
            org_id, installation_id, getattr(current_user, "username", "system")
        )
        if not res.get("ok"):
            return error_response("UNINSTALL_FAILED", res.get("error", "Unknown error"))
        return success_response(res)
    except Exception as e:
        return error_response("UNINSTALL_ERROR", str(e))


@router.post("/installations/{installation_id}/run")
def api_run(
    installation_id: str,
    body: RunPluginRequest,
    current_user: Any = Depends(
        require_permissions([Permission.marketplace_run_plugin])
    ),
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        org_id = getattr(tenant, "organization_id", "default")
        res = run_plugin_action(
            org_id,
            installation_id,
            body.action,
            body.payload,
            getattr(current_user, "username", "system"),
        )
        if not res.get("ok"):
            return error_response("RUN_FAILED", res.get("error", "Unknown error"))
        return success_response(res)
    except Exception as e:
        return error_response("RUN_ERROR", str(e))


@router.post("/manifest")
def api_register_manifest(
    body: RegisterManifestRequest,
    current_user: AuthSession = Depends(
        require_permissions([Permission.marketplace_manage])
    ),
):
    try:
        if getattr(current_user, "role", "") != "admin":
            return error_response(
                "FORBIDDEN", "Only administrators can register manifests"
            )

        manifest_dict = body.model_dump()
        ok, errors = validate_plugin_manifest(manifest_dict)
        if not ok:
            return error_response("VALIDATION_FAILED", "; ".join(errors))

        manifest = PluginManifest(
            name=body.name,
            slug=body.slug,
            version=body.version,
            description=body.description,
            author=body.author,
            category=body.category,
            status=body.status,
            required_features=body.required_features,
            required_permissions=body.required_permissions,
            config_schema=body.config_schema,
            default_config=body.default_config,
            entrypoint=body.entrypoint,
            safety_level=body.safety_level,
            metadata_json=body.metadata,
        )

        with SessionLocal() as db:
            result = register_plugin_manifest(
                db, manifest, getattr(current_user, "username", "system")
            )

        return success_response({"manifest": result})
    except Exception as e:
        return error_response("REGISTER_ERROR", str(e))
