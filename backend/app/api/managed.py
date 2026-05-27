from fastapi import APIRouter
from app.core.responses import success_response

router = APIRouter(prefix="/api/managed", tags=["managed"])


@router.get("/status")
def status():
    return success_response({"enabled": True, "msp_mode": False})


@router.get("/overview")
def overview():
    return success_response({"tenants": []})
