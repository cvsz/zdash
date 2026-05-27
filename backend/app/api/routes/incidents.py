from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.models import AuthSession
from app.core.responses import ok
from app.services.incidents import get_incident_service

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("")
async def list_incidents(user: AuthSession = Depends(get_current_user)) -> dict:
    _ = user
    return ok(get_incident_service().list_incidents())


@router.post("")
async def create_incident(payload: dict, user: AuthSession = Depends(get_current_user)) -> dict:
    if user.role not in {"operator", "admin"}:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    item = await get_incident_service().create_incident(title=str(payload.get("title", "Untitled Incident")), severity=str(payload.get("severity", "warning")), notes=str(payload.get("notes", "")), actor=user.username)
    return ok(item)


@router.post("/{incident_id}/ack")
async def ack_incident(incident_id: str, user: AuthSession = Depends(get_current_user)) -> dict:
    if user.role not in {"operator", "admin"}:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return ok(await get_incident_service().acknowledge_incident(incident_id, user.username))


@router.post("/{incident_id}/resolve")
async def resolve_incident(incident_id: str, payload: dict, user: AuthSession = Depends(get_current_user)) -> dict:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return ok(await get_incident_service().resolve_incident(incident_id, user.username, str(payload.get("notes", ""))))
