from fastapi import Header,HTTPException
from app.core.config import get_settings
from .tenant_context import TenantContext

def get_tenant_context(x_zdash_tenant:str|None=Header(default=None),x_zdash_workspace:str|None=Header(default=None)):
    s=get_settings()
    org=x_zdash_tenant or "default-org"
    ws=x_zdash_workspace or "default-workspace"
    if s.multi_tenant_enabled and (not org or not ws):
        raise HTTPException(status_code=400,detail="Missing tenant context")
    return TenantContext(organization_id=org,workspace_id=ws)
