from fastapi import APIRouter
from app.core.responses import ok
from app.long_horizon.horizon_report_service import horizon_report

router = APIRouter(prefix="/api/long-horizon", tags=["long-horizon"])


@router.get("/report")
def report():
    return ok(horizon_report())
