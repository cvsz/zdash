from fastapi import APIRouter, Header, HTTPException
from app.core.responses import ok
from app.developer.api_key_service import service

router = APIRouter(prefix="/partner/v1", tags=["partner"])

def _require_key(x_zdash_api_key: str | None = Header(default=None)):
    if not x_zdash_api_key:
        raise HTTPException(status_code=401, detail="API_KEY_INVALID")
    key = service.authenticate_raw_key(x_zdash_api_key)
    if not key:
        raise HTTPException(status_code=401, detail="API_KEY_INVALID")
    return key

@router.get("/health")
def health(x_zdash_api_key: str | None = Header(default=None)):
    _require_key(x_zdash_api_key)
    return ok({"status": "ok", "sandbox": True})

@router.get("/me")
def me(x_zdash_api_key: str | None = Header(default=None)):
    key = _require_key(x_zdash_api_key)
    return ok({"organization_id": key.organization_id, "workspace_id": key.workspace_id, "scopes": key.scopes})
