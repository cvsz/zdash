from fastapi import Header, HTTPException

from app.core.config import get_settings
from .tenant_context import TenantContext


def get_tenant_context(
    x_zdash_tenant: str | None = Header(default=None),
    x_zdash_workspace: str | None = Header(default=None),
):
    settings = get_settings()
    org = str(x_zdash_tenant or getattr(settings, "default_tenant_id", "default-org"))
    workspace = str(x_zdash_workspace or getattr(
        settings, "default_workspace_id", "default-workspace"
    ))

    if getattr(settings, "multi_tenant_enabled", False) and (not org or not workspace):
        raise HTTPException(status_code=400, detail="Missing tenant context")

    return TenantContext(organization_id=org, workspace_id=workspace)
