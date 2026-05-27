from fastapi import APIRouter
from app.core.responses import success_response
from app.ops.health_analyzer import HealthAnalyzer
from app.ops.ops_autopilot import OpsAutopilot

router = APIRouter(prefix="/api/ops", tags=["ops"])
ha = HealthAnalyzer()
ap = OpsAutopilot(ha)


@router.get("/status")
def status():
    return success_response({"enabled": True, "mode": "advisory", "dry_run": True})


@router.post("/evaluate")
def evaluate():
    return success_response(ap.evaluate_system("org-default", "ws-default"))


@router.get("/health")
def health():
    return success_response([s.model_dump() for s in ha.snapshots])


@router.get("/autopilot/status")
def auto_status():
    return success_response(ap.get_autopilot_status())
