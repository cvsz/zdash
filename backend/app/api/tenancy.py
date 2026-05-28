from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth.dependencies import get_current_user
from app.auth.models import AuthSession
from app.core.events import event_bus
from app.core.responses import ok
from app.tenancy.dependencies import get_tenant_context
from app.tenancy.models import (
    MemberCreateRequest,
    OrganizationCreateRequest,
    OrganizationUpdateRequest,
    WorkspaceCreateRequest,
    WorkspaceUpdateRequest,
)
from app.tenancy.tenant_service import service as tenant_service

router = APIRouter(prefix="/api/tenancy", tags=["tenancy"])


def _audit(action: str, actor: AuthSession, metadata: dict) -> None:
    event_bus.emit(
        "tenancy.admin.changed",
        "tenancy.api",
        action,
        {"action": action, "actor": actor.username, **metadata},
    )


def _require_org_admin(organization_id: str, user: AuthSession) -> None:
    if tenant_service.is_organization_admin(organization_id, user):
        return
    raise HTTPException(status_code=403, detail="Organization admin access required")


@router.get("/context")
def context(
    tenant_context=Depends(get_tenant_context),
) -> dict:
    return ok({"context": tenant_context.__dict__})


@router.get("/organizations")
def organizations(user: AuthSession = Depends(get_current_user)) -> dict:
    items = [item.model_dump() for item in tenant_service.list_accessible_organizations(user)]
    return ok({"items": items})


@router.post("/organizations")
def create_organization(
    payload: OrganizationCreateRequest,
    user: AuthSession = Depends(get_current_user),
) -> dict:
    organization = tenant_service.create_organization(payload, user)
    _audit("organization.create", user, {"organization_id": organization.id})
    return ok({"item": organization.model_dump()})


@router.get("/organizations/{organization_id}")
def get_organization(
    organization_id: str,
    user: AuthSession = Depends(get_current_user),
) -> dict:
    organization = tenant_service.get_organization(organization_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="organization not found")
    if user.role != "admin" and organization not in tenant_service.list_accessible_organizations(user):
        raise HTTPException(status_code=403, detail="Organization access denied")
    return ok({"item": organization.model_dump()})


@router.patch("/organizations/{organization_id}")
def patch_organization(
    organization_id: str,
    payload: OrganizationUpdateRequest,
    user: AuthSession = Depends(get_current_user),
) -> dict:
    _require_org_admin(organization_id, user)
    updated = tenant_service.update_organization(organization_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="organization not found")
    _audit("organization.update", user, {"organization_id": organization_id})
    return ok({"item": updated.model_dump()})


@router.get("/organizations/{organization_id}/workspaces")
def list_workspaces(
    organization_id: str,
    user: AuthSession = Depends(get_current_user),
) -> dict:
    organization = tenant_service.get_organization(organization_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="organization not found")
    if user.role != "admin" and organization not in tenant_service.list_accessible_organizations(user):
        raise HTTPException(status_code=403, detail="Organization access denied")
    items = [workspace.model_dump() for workspace in tenant_service.list_workspaces(organization_id)]
    return ok({"items": items})


@router.post("/organizations/{organization_id}/workspaces")
def create_workspace(
    organization_id: str,
    payload: WorkspaceCreateRequest,
    user: AuthSession = Depends(get_current_user),
) -> dict:
    _require_org_admin(organization_id, user)
    try:
        workspace = tenant_service.create_workspace(organization_id, payload, user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    _audit("workspace.create", user, {"workspace_id": workspace.id})
    return ok({"item": workspace.model_dump()})


@router.get("/workspaces/{workspace_id}")
def get_workspace(
    workspace_id: str,
    user: AuthSession = Depends(get_current_user),
) -> dict:
    workspace = tenant_service.get_workspace(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="workspace not found")
    if not tenant_service.can_access_workspace(workspace_id, user):
        raise HTTPException(status_code=403, detail="Workspace access denied")
    return ok({"item": workspace.model_dump()})


@router.patch("/workspaces/{workspace_id}")
def patch_workspace(
    workspace_id: str,
    payload: WorkspaceUpdateRequest,
    user: AuthSession = Depends(get_current_user),
) -> dict:
    workspace = tenant_service.get_workspace(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="workspace not found")
    _require_org_admin(workspace.organization_id, user)
    updated = tenant_service.update_workspace(workspace_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="workspace not found")
    _audit("workspace.update", user, {"workspace_id": workspace_id})
    return ok({"item": updated.model_dump()})


@router.post("/organizations/{organization_id}/members")
def add_organization_member(
    organization_id: str,
    payload: MemberCreateRequest,
    user: AuthSession = Depends(get_current_user),
) -> dict:
    _require_org_admin(organization_id, user)
    try:
        member = tenant_service.add_organization_member(organization_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    _audit(
        "organization.member.add",
        user,
        {"organization_id": organization_id, "member_user_id": payload.user_id},
    )
    return ok({"item": member.model_dump()})


@router.post("/workspaces/{workspace_id}/members")
def add_workspace_member(
    workspace_id: str,
    payload: MemberCreateRequest,
    user: AuthSession = Depends(get_current_user),
) -> dict:
    workspace = tenant_service.get_workspace(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="workspace not found")
    _require_org_admin(workspace.organization_id, user)
    try:
        member = tenant_service.add_workspace_member(workspace_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    _audit(
        "workspace.member.add",
        user,
        {"workspace_id": workspace_id, "member_user_id": payload.user_id},
    )
    return ok({"item": member.model_dump()})
