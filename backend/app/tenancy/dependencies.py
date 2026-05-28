from fastapi import Depends, HTTPException, Request
from app.auth.dependencies import get_current_user
from app.auth.models import AuthSession
from app.core.config import get_settings
from app.tenancy.tenant_context import TenantContext
from app.tenancy.tenant_service import service


def get_tenant_context(
    request: Request,
    user: AuthSession = Depends(get_current_user),
) -> TenantContext:
    settings = get_settings()
    tenant_header = request.headers.get(settings.tenant_header_name)
    workspace_header = request.headers.get(settings.workspace_header_name)
    try:
        return service.resolve_context(
            user,
            organization_id=tenant_header,
            workspace_id=workspace_header,
            source="headers",
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


def require_workspace_access(
    workspace_id: str,
    user: AuthSession,
) -> None:
    if service.can_access_workspace(workspace_id, user):
        return
    raise HTTPException(status_code=403, detail="Workspace access denied")
