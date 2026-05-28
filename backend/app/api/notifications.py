from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.models import AuthSession
from app.auth.rbac import Permission, has_permission
from app.core.events import event_bus
from app.core.responses import ok
from app.notifications.models import (
    AlertRuleCreateRequest,
    AlertRuleUpdateRequest,
    NotificationChannelCreateRequest,
    NotificationChannelUpdateRequest,
    NotificationTestRequest,
)
from app.notifications.notification_service import get_notification_service
from app.tenancy.dependencies import get_tenant_context

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def _require_read_access(user: AuthSession) -> None:
    if has_permission(user.role, Permission.READ_NOTIFICATIONS):
        return
    raise HTTPException(status_code=403, detail="Insufficient permissions")


def _require_manage_access(user: AuthSession) -> None:
    if has_permission(user.role, Permission.MANAGE_NOTIFICATIONS):
        return
    raise HTTPException(status_code=403, detail="Insufficient permissions")


def _audit(action: str, actor: AuthSession, metadata: dict) -> None:
    event_bus.emit(
        "notification.config.changed",
        "notifications.api",
        action,
        {"action": action, "actor": actor.username, **metadata},
    )


@router.get("/status")
def status(
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    _require_read_access(user)
    service = get_notification_service()
    service.ensure_defaults(
        tenant_context.organization_id,
        tenant_context.workspace_id,
    )
    return ok(
        {
            **service.status(),
            "organization_id": tenant_context.organization_id,
            "workspace_id": tenant_context.workspace_id,
        }
    )


@router.get("/rules")
def rules(
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    _require_read_access(user)
    service = get_notification_service()
    service.ensure_defaults(tenant_context.organization_id, tenant_context.workspace_id)
    items = [
        rule.model_dump()
        for rule in service.rules_for_tenant(
            tenant_context.organization_id,
            tenant_context.workspace_id,
        )
    ]
    return ok({"items": items})


@router.post("/rules")
def create_rule(
    payload: AlertRuleCreateRequest,
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    _require_manage_access(user)
    service = get_notification_service()
    rule = service.create_rule(
        tenant_context.organization_id,
        tenant_context.workspace_id,
        payload,
    )
    _audit("rule.create", user, {"rule_id": rule.id})
    return ok({"item": rule.model_dump()})


@router.patch("/rules/{rule_id}")
def patch_rule(
    rule_id: str,
    payload: AlertRuleUpdateRequest,
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    _require_manage_access(user)
    service = get_notification_service()
    rule = service.rules.get(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="rule not found")
    if (
        rule.organization_id != tenant_context.organization_id
        or rule.workspace_id != tenant_context.workspace_id
    ):
        raise HTTPException(status_code=403, detail="cross-tenant rule access denied")
    updated = service.update_rule(rule_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="rule not found")
    _audit("rule.update", user, {"rule_id": rule_id})
    return ok({"item": updated.model_dump()})


@router.delete("/rules/{rule_id}")
def delete_rule(
    rule_id: str,
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    _require_manage_access(user)
    service = get_notification_service()
    rule = service.rules.get(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="rule not found")
    if (
        rule.organization_id != tenant_context.organization_id
        or rule.workspace_id != tenant_context.workspace_id
    ):
        raise HTTPException(status_code=403, detail="cross-tenant rule access denied")
    deleted = service.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="rule not found")
    _audit("rule.delete", user, {"rule_id": rule_id})
    return ok({"deleted": True})


@router.get("/events")
def events(
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    _require_read_access(user)
    service = get_notification_service()
    items = [
        event.model_dump()
        for event in service.events_for_tenant(
            tenant_context.organization_id,
            tenant_context.workspace_id,
        )
    ]
    return ok({"items": items})


@router.get("/channels")
def channels(
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    _require_read_access(user)
    service = get_notification_service()
    service.ensure_defaults(tenant_context.organization_id, tenant_context.workspace_id)
    items = [
        channel.model_dump()
        for channel in service.channels_for_tenant(
            tenant_context.organization_id,
            tenant_context.workspace_id,
        )
    ]
    return ok({"items": items})


@router.post("/channels")
def create_channel(
    payload: NotificationChannelCreateRequest,
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    _require_manage_access(user)
    service = get_notification_service()
    channel = service.create_channel(
        tenant_context.organization_id,
        tenant_context.workspace_id,
        payload,
    )
    _audit("channel.create", user, {"channel_id": channel.id})
    return ok({"item": channel.model_dump()})


@router.patch("/channels/{channel_id}")
def patch_channel(
    channel_id: str,
    payload: NotificationChannelUpdateRequest,
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    _require_manage_access(user)
    service = get_notification_service()
    channel = service.channels.get(channel_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="channel not found")
    if (
        channel.organization_id != tenant_context.organization_id
        or channel.workspace_id != tenant_context.workspace_id
    ):
        raise HTTPException(status_code=403, detail="cross-tenant channel access denied")
    updated = service.update_channel(channel_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="channel not found")
    _audit("channel.update", user, {"channel_id": channel_id})
    return ok({"item": updated.model_dump()})


@router.delete("/channels/{channel_id}")
def delete_channel(
    channel_id: str,
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    _require_manage_access(user)
    service = get_notification_service()
    channel = service.channels.get(channel_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="channel not found")
    if (
        channel.organization_id != tenant_context.organization_id
        or channel.workspace_id != tenant_context.workspace_id
    ):
        raise HTTPException(status_code=403, detail="cross-tenant channel access denied")
    deleted = service.delete_channel(channel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="channel not found")
    _audit("channel.delete", user, {"channel_id": channel_id})
    return ok({"deleted": True})


@router.post("/test")
def test_notification(
    payload: NotificationTestRequest,
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    _require_manage_access(user)
    service = get_notification_service()
    result = service.send_test_notification(
        organization_id=tenant_context.organization_id,
        workspace_id=tenant_context.workspace_id,
        actor_user_id=user.username,
        title=payload.title,
        message=payload.message,
        payload=payload.payload,
    )
    return ok({"result": result})
