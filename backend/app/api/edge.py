from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(prefix="/api/edge", tags=["edge"])


@router.get("/status")
def status():
    return {
        "ok": True,
        "data": {"enabled": True, "dry_run": True},
        "error": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
