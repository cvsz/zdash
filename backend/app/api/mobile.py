from fastapi import APIRouter
from app.core.responses import ok

router = APIRouter(prefix="/api/mobile", tags=["mobile"])


@router.get("/status")
def status():
    return ok({"enabled": True, "push": {"enabled": False, "provider": "mock"}})


@router.get("/home")
def home():
    return ok(
        {
            "status": "healthy",
            "risk": {"halted": False},
            "incidents": 0,
            "approvals": 0,
            "alerts": [],
        }
    )
