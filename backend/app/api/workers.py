from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.models import AuthSession
from app.auth.rbac import Permission, has_permission
from app.core.events import event_bus
from app.core.responses import ok
from app.tenancy.dependencies import get_tenant_context
from app.workers.models import WorkerTaskCreateRequest
from app.workers.queue import queue

router = APIRouter(prefix="/api/workers", tags=["workers"])


_TASK_PERMISSION_MAP: dict[str, Permission] = {
    "trading_scan": Permission.RUN_DRY_RUN_TRADING,
    "risk_check": Permission.READ_RISK,
    "backtest_run": Permission.RUN_BACKTESTS,
    "optimization_run": Permission.RUN_BACKTESTS,
    "content_pipeline_run": Permission.MANAGE_CONTENT_APPROVAL,
    "content_publish_dry_run": Permission.MANAGE_CONTENT_APPROVAL,
    "iot_status_check": Permission.CONTROL_DRY_RUN_IOT,
    "notification_dispatch": Permission.MANAGE_NOTIFICATIONS,
    "audit_compaction": Permission.MANAGE_WORKERS,
    "backup_run": Permission.MANAGE_WORKERS,
    "custom": Permission.MANAGE_WORKERS,
}


def _require_task_permission(task_type: str, user: AuthSession) -> None:
    required_permission = _TASK_PERMISSION_MAP.get(task_type, Permission.MANAGE_WORKERS)
    if has_permission(user.role, required_permission):
        return
    raise HTTPException(status_code=403, detail="Insufficient permissions for task type")


@router.get("/status")
def status(
    tenant_context=Depends(get_tenant_context),
    _: AuthSession = Depends(get_current_user),
):
    snapshot = queue.status_snapshot()
    snapshot["tenant"] = {
        "organization_id": tenant_context.organization_id,
        "workspace_id": tenant_context.workspace_id,
    }
    return ok(snapshot)


@router.get("/tasks")
def tasks(
    tenant_context=Depends(get_tenant_context),
    _: AuthSession = Depends(get_current_user),
):
    items = queue.list_tasks(tenant_context.organization_id, tenant_context.workspace_id)
    return ok({"items": [item.model_dump() for item in items]})


@router.post("/tasks")
def create(
    payload: WorkerTaskCreateRequest,
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    _require_task_permission(payload.task_type, user)
    task = queue.enqueue(
        payload.task_type,
        payload.payload,
        tenant_context,
        priority=payload.priority,
    )
    event_bus.emit(
        "worker.task.enqueued",
        "workers.api",
        "worker task enqueued",
        {
            "task_id": task.id,
            "task_type": task.task_type,
            "organization_id": tenant_context.organization_id,
            "workspace_id": tenant_context.workspace_id,
            "actor": user.username,
        },
    )
    return ok({"item": task.model_dump()})


@router.get("/tasks/{task_id}")
def task_detail(
    task_id: str,
    tenant_context=Depends(get_tenant_context),
    _: AuthSession = Depends(get_current_user),
):
    task = queue.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if task.organization_id != tenant_context.organization_id or task.workspace_id != tenant_context.workspace_id:
        raise HTTPException(status_code=403, detail="cross-tenant task access denied")
    return ok({"item": task.model_dump()})


@router.post("/tasks/{task_id}/cancel")
def cancel_task(
    task_id: str,
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    if not has_permission(user.role, Permission.MANAGE_WORKERS):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    task = queue.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if task.organization_id != tenant_context.organization_id or task.workspace_id != tenant_context.workspace_id:
        raise HTTPException(status_code=403, detail="cross-tenant task access denied")
    updated = queue.cancel(task_id)
    event_bus.emit(
        "worker.task.cancelled",
        "workers.api",
        "worker task cancelled",
        {"task_id": task_id, "actor": user.username},
    )
    return ok({"item": updated.model_dump()})


@router.post("/tasks/{task_id}/retry")
def retry_task(
    task_id: str,
    tenant_context=Depends(get_tenant_context),
    user: AuthSession = Depends(get_current_user),
):
    if not has_permission(user.role, Permission.MANAGE_WORKERS):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    task = queue.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    if task.organization_id != tenant_context.organization_id or task.workspace_id != tenant_context.workspace_id:
        raise HTTPException(status_code=403, detail="cross-tenant task access denied")
    updated = queue.retry(task_id)
    event_bus.emit(
        "worker.task.retry",
        "workers.api",
        "worker task retried",
        {"task_id": task_id, "actor": user.username},
    )
    return ok({"item": updated.model_dump()})
