from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.audit.audit_service import AuditService
from app.audit.models import AuditLogCreate
from app.auth.models import AuthSession
from app.auth.dependencies import require_authenticated, require_permission
from app.auth.rbac import Permission
from app.core.responses import fail, ok
from app.core.events import event_bus
from app.db.session import get_db_session
from app.observability.metrics import metrics_store
from app.risk.guardian_service import get_guardian_service
from app.risk.models import AccountSnapshot
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/risk", tags=["risk"])


def _actor_email(current_user: object) -> str:
    if isinstance(current_user, AuthSession):
        return current_user.username
    return "system"


def _maybe_audit(session: object, entry: AuditLogCreate) -> None:
    if isinstance(session, Session):
        AuditService(session).log(entry)


class HaltRequest(BaseModel):
    reason: str = Field(min_length=1)


class ResumeRequest(BaseModel):
    reason: str = Field(min_length=1)
    approved: bool = False


class ApproveExecutionRequest(BaseModel):
    signal: dict[str, Any]
    snapshot: AccountSnapshot


@router.get("/status")
def status(_: object = Depends(require_authenticated)) -> dict:
    service = get_guardian_service()
    return ok(service.get_status())


@router.post("/check")
def check(
    snapshot: AccountSnapshot,
    _: object = Depends(require_authenticated),
) -> dict:
    service = get_guardian_service()
    decision = service.check(snapshot)
    return ok({"decision": decision.model_dump(mode="json")})


@router.get("/drawdown")
def drawdown(_: object = Depends(require_authenticated)) -> dict:
    service = get_guardian_service()
    latest = service.latest_drawdown()
    if latest is None:
        safe = service.check(
            AccountSnapshot(
                balance=10000.0,
                equity=10000.0,
                peak_equity=10000.0,
                daily_start_equity=10000.0,
                open_positions=0,
                floating_pnl=0.0,
                realized_pnl_today=0.0,
                timestamp=datetime.now(timezone.utc),
            )
        )
        latest = safe.drawdown
    return ok({"drawdown": latest.model_dump(mode="json") if latest else None})


@router.post("/halt")
def halt(
    req: HaltRequest,
    current_user: AuthSession = Depends(require_permission(Permission.HALT_RESUME_RISK)),
    session: Session = Depends(get_db_session),
) -> dict:
    service = get_guardian_service()
    try:
        state = service.halt(req.reason, source="manual")
    except ValueError as exc:
        return fail("RISK_HALT_INVALID", str(exc))
    metrics_store.set_risk_halt_active(True)
    event_bus.emit(
        "risk.halt",
        "RiskAPI",
        "Manual risk halt activated",
        {"reason": req.reason, "source": "manual"},
    )
    _maybe_audit(
        session,
        AuditLogCreate(
            actor_user_id="",
            actor_email=_actor_email(current_user),
            action="risk.halt",
            resource_type="risk",
            resource_id="halt_state",
            result="success",
            metadata={"reason": req.reason, "source": "manual"},
        ),
    )
    return ok({"halt_state": state.model_dump(mode="json")})


@router.post("/resume")
def resume(
    req: ResumeRequest,
    current_user: AuthSession = Depends(require_permission(Permission.HALT_RESUME_RISK)),
    session: Session = Depends(get_db_session),
) -> dict:
    service = get_guardian_service()
    try:
        state = service.resume(reason=req.reason, approved=req.approved)
    except ValueError as exc:
        return fail("RISK_RESUME_INVALID", str(exc))
    metrics_store.set_risk_halt_active(False)
    event_bus.emit(
        "risk.resume",
        "RiskAPI",
        "Manual risk halt resumed",
        {"reason": req.reason, "approved": req.approved},
    )
    _maybe_audit(
        session,
        AuditLogCreate(
            actor_user_id="",
            actor_email=_actor_email(current_user),
            action="risk.resume",
            resource_type="risk",
            resource_id="halt_state",
            result="success",
            metadata={"reason": req.reason, "approved": req.approved},
        ),
    )
    return ok({"halt_state": state.model_dump(mode="json")})


@router.post("/approve-execution")
def approve_execution(
    req: ApproveExecutionRequest,
    _: object = Depends(require_authenticated),
) -> dict:
    service = get_guardian_service()
    decision = service.approve_execution(signal=req.signal, snapshot=req.snapshot)
    return ok({"decision": decision.model_dump(mode="json")})
