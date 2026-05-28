from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, field_validator

from app.auth.dependencies import require_permission
from app.auth.models import AuthSession
from app.auth.rbac import Permission
from app.core.responses import ok

router = APIRouter(prefix="/api/workspaces/federation", tags=["workspaces-federation"])
_peers: list[dict] = []


class FederationRegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=64)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("name is required")
        return normalized


@router.get("/status")
def status():
    return ok({"mode": "mock", "dry_run": True, "network_enabled": False})


@router.get("/peers")
def peers(_: AuthSession = Depends(require_permission(Permission.READ_TENANCY))):
    return ok({"items": _peers})


@router.post("/register")
def register(
    payload: FederationRegisterRequest,
    _: AuthSession = Depends(require_permission(Permission.MANAGE_TENANCY)),
):
    peer = {"name": payload.name, "registered": True, "active": False}
    _peers.append(peer)
    return ok({"item": peer, "note": "mock-only; no outbound federation traffic"})
