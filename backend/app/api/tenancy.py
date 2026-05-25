from fastapi import APIRouter,Depends
from app.tenancy.dependencies import get_tenant_context
from app.core.responses import ok

router=APIRouter(prefix="/api/tenancy",tags=["tenancy"])
@router.get("/context")
def context(tc=Depends(get_tenant_context)): return ok(tc.__dict__)
@router.get("/organizations")
def orgs(): return ok([])
