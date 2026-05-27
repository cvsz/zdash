from fastapi import APIRouter
from app.core.responses import ok

router = APIRouter(prefix="/api/workspaces/federation", tags=["workspaces-federation"])
_peers: list[dict] = []

@router.get('/status')
def status():
    return ok({"mode": "mock", "dry_run": True, "network_enabled": False})

@router.get('/peers')
def peers():
    return ok({"items": _peers})

@router.post('/register')
def register(payload: dict):
    peer = {"name": str(payload.get('name','peer')), "registered": True, "active": False}
    _peers.append(peer)
    return ok({"item": peer, "note": "mock-only; no outbound federation traffic"})
