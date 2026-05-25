from fastapi import APIRouter,Depends
from app.tenancy.dependencies import get_tenant_context
from app.core.responses import ok
from app.workers.queue import queue,TASKS

router=APIRouter(prefix="/api/workers",tags=["workers"])
@router.get("/status")
def status(): return ok({"queued":len([t for t in TASKS.values() if t.status=="queued"])})
@router.get("/tasks")
def tasks(tc=Depends(get_tenant_context)): return ok([t.model_dump() for t in queue.list_tasks(tc.organization_id,tc.workspace_id)])
@router.post("/tasks")
def create(payload:dict,tc=Depends(get_tenant_context)): return ok(queue.enqueue(payload.get("task_type","custom"),payload.get("payload",{}),tc).model_dump())
