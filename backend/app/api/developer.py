from fastapi import APIRouter
from app.core.responses import ok
from app.developer.api_key_service import service
from app.developer.models import ApiKeyCreateRequest

router = APIRouter(prefix="/api/developer", tags=["developer"])

def _tenant():
    return {"organization_id": "org_default", "workspace_id": "ws_default"}

@router.get("/status")
def status():
    return ok({"enabled": True, "sandbox_default": True})

@router.get("/api-keys")
def list_api_keys():
    return ok([k.model_dump(exclude={"key_hash"}) for k in service.list_api_keys(_tenant())])

@router.post("/api-keys")
def create_api_key(request: ApiKeyCreateRequest):
    return ok(service.create_api_key(request, "system", _tenant()).model_dump())
