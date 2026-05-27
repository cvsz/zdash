from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.audit.audit_service import AuditService
from app.audit.models import AuditLogCreate
from app.auth.dependencies import require_authenticated, require_permission
from app.auth.models import AuthSession
from app.auth.rbac import Permission
from app.core.config import get_settings
from app.core.responses import ok
from app.db.session import get_db_session
from app.iot.iot_service import IoTService
from app.iot.models import IoTAction, IoTPowerCycleRequest
from app.observability.metrics import metrics_store

router = APIRouter(prefix="/api/iot", tags=["iot"])


def _service() -> IoTService:
    return IoTService()


def _actor_email(current_user: object) -> str:
    if isinstance(current_user, AuthSession):
        return current_user.username
    return "system"


def _maybe_audit(session: object, entry: AuditLogCreate) -> None:
    if isinstance(session, Session):
        AuditService(session).log(entry)


@router.get("/status")
def status(
    device_alias: str | None = None,
    _: object = Depends(require_authenticated),
) -> dict:
    result = _service().get_status(device_alias=device_alias)
    return ok({"result": result.model_dump(mode="json")})


@router.post("/action")
def action(
    req: IoTAction,
    current_user: AuthSession = Depends(require_permission(Permission.CONTROL_DRY_RUN_IOT)),
    session: Session = Depends(get_db_session),
) -> dict:
    result = _service().execute(req)
    metrics_store.increment_iot_actions()
    _maybe_audit(
        session,
        AuditLogCreate(
            actor_user_id="",
            actor_email=_actor_email(current_user),
            action="iot.action.requested",
            resource_type="iot",
            resource_id=req.device_alias,
            metadata={"action": req.action, "confirmation": req.confirmation},
        ),
    )
    return ok({"result": result.model_dump(mode="json")})


@router.post("/power-cycle")
def power_cycle(
    req: IoTPowerCycleRequest | None = None,
    current_user: AuthSession = Depends(require_permission(Permission.CONTROL_DRY_RUN_IOT)),
    session: Session = Depends(get_db_session),
) -> dict:
    settings = get_settings()
    request = req or IoTPowerCycleRequest(
        device_alias=settings.tapo_device_alias, confirmation=False
    )
    result = _service().power_cycle(
        device_alias=request.device_alias, confirmation=request.confirmation
    )
    metrics_store.increment_iot_actions()
    _maybe_audit(
        session,
        AuditLogCreate(
            actor_user_id="",
            actor_email=_actor_email(current_user),
            action="iot.action.requested",
            resource_type="iot",
            resource_id=request.device_alias,
            metadata={"action": "power_cycle", "confirmation": request.confirmation},
        ),
    )
    return ok({"result": result.model_dump(mode="json")})
