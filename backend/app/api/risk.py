from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.responses import fail, ok
from app.risk.guardian_service import get_guardian_service
from app.risk.models import AccountSnapshot

router = APIRouter(prefix="/api/risk", tags=["risk"])


class HaltRequest(BaseModel):
    reason: str = Field(min_length=1)


class ResumeRequest(BaseModel):
    reason: str = Field(min_length=1)
    approved: bool = False


class ApproveExecutionRequest(BaseModel):
    signal: dict[str, Any]
    snapshot: AccountSnapshot


@router.get("/status")
def status() -> dict:
    service = get_guardian_service()
    return ok(service.get_status())


@router.post("/check")
def check(snapshot: AccountSnapshot) -> dict:
    service = get_guardian_service()
    decision = service.check(snapshot)
    return ok({"decision": decision.model_dump(mode="json")})


@router.get("/drawdown")
def drawdown() -> dict:
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
def halt(req: HaltRequest) -> dict:
    service = get_guardian_service()
    try:
        state = service.halt(req.reason, source="manual")
    except ValueError as exc:
        return fail("RISK_HALT_INVALID", str(exc))
    return ok({"halt_state": state.model_dump(mode="json")})


@router.post("/resume")
def resume(req: ResumeRequest) -> dict:
    service = get_guardian_service()
    try:
        state = service.resume(reason=req.reason, approved=req.approved)
    except ValueError as exc:
        return fail("RISK_RESUME_INVALID", str(exc))
    return ok({"halt_state": state.model_dump(mode="json")})


@router.post("/approve-execution")
def approve_execution(req: ApproveExecutionRequest) -> dict:
    service = get_guardian_service()
    decision = service.approve_execution(signal=req.signal, snapshot=req.snapshot)
    return ok({"decision": decision.model_dump(mode="json")})
