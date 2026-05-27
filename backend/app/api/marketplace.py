from fastapi import APIRouter, Depends, Header
from app.core.responses import ok
from app.core.auth import get_current_user
from app.marketplace.plugin_registry import list_plugins, get_plugin
from app.marketplace.plugin_service import (
    list_installations,
    install_plugin,
    enable_plugin,
    disable_plugin,
    uninstall_plugin,
    run_plugin_action,
)

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])


def _org(o):
    return o or "default-org"


@router.get("/plugins")
def plugins(user=Depends(get_current_user)):
    return ok({"plugins": [p.__dict__ for p in list_plugins()]})


@router.get("/plugins/{plugin_id}")
def plugin(plugin_id: str, user=Depends(get_current_user)):
    p = get_plugin(plugin_id)
    return ok({"plugin": p.__dict__ if p else None})


@router.get("/installations")
def installations(
    user=Depends(get_current_user), x_organization_id: str | None = Header(default=None)
):
    return ok({"installations": list_installations(_org(x_organization_id))})


@router.post("/install")
def install(
    body: dict,
    user=Depends(get_current_user),
    x_organization_id: str | None = Header(default=None),
):
    return ok(
        install_plugin(
            _org(x_organization_id),
            body["plugin_id"],
            body.get("workspace_id", "default"),
            body.get("config"),
        )
    )


@router.post("/installations/{installation_id}/enable")
def enable(installation_id: str, user=Depends(get_current_user)):
    return ok(enable_plugin(installation_id))


@router.post("/installations/{installation_id}/disable")
def disable(installation_id: str, user=Depends(get_current_user)):
    return ok(disable_plugin(installation_id))


@router.delete("/installations/{installation_id}")
def uninstall(installation_id: str, user=Depends(get_current_user)):
    return ok(uninstall_plugin(installation_id))


@router.post("/installations/{installation_id}/run")
def run(installation_id: str, body: dict, user=Depends(get_current_user)):
    return ok(
        run_plugin_action(
            installation_id, body.get("action", "status"), body.get("payload", {})
        )
    )
