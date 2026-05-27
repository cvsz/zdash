from fastapi import APIRouter
from app.core.responses import ok

router = APIRouter(prefix="/api/continuous-planning", tags=["continuous-planning"])


@router.get("/status")
def status():
    return ok({"enabled": True, "dry_run": True, "requires_approval": True})
