from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.responses import ok
from app.iot.iot_service import IoTService
from app.iot.models import IoTAction, IoTPowerCycleRequest

router = APIRouter(prefix="/api/iot", tags=["iot"])


def _service() -> IoTService:
    return IoTService()


@router.get("/status")
def status(device_alias: str | None = None) -> dict:
    result = _service().get_status(device_alias=device_alias)
    return ok({"result": result.model_dump(mode="json")})


@router.post("/action")
def action(req: IoTAction) -> dict:
    result = _service().execute(req)
    return ok({"result": result.model_dump(mode="json")})


@router.post("/power-cycle")
def power_cycle(req: IoTPowerCycleRequest | None = None) -> dict:
    settings = get_settings()
    request = req or IoTPowerCycleRequest(
        device_alias=settings.tapo_device_alias, confirmation=False
    )
    result = _service().power_cycle(
        device_alias=request.device_alias, confirmation=request.confirmation
    )
    return ok({"result": result.model_dump(mode="json")})
