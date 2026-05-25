import uuid
from .models import WorkerTask

TASKS={}
QUEUE=[]

class WorkerQueue:
    def enqueue(self,task_type,payload,tenant_context,priority=5):
        t=WorkerTask(id=str(uuid.uuid4()),organization_id=tenant_context.organization_id,workspace_id=tenant_context.workspace_id,task_type=task_type,payload=payload or {},priority=priority)
        TASKS[t.id]=t; QUEUE.append(t.id); return t
    def dequeue(self,worker_id):
        if not QUEUE: return None
        t=TASKS[QUEUE.pop(0)]; t.status="running"; t.attempts+=1; return t
    def complete(self,task_id,result): t=TASKS[task_id]; t.status="completed"; t.result=result; return t
    def fail(self,task_id,error): t=TASKS[task_id]; t.status="failed"; t.error=error; return t
    def retry(self,task_id): t=TASKS[task_id]; t.status="retrying"; QUEUE.append(task_id); return t
    def cancel(self,task_id): t=TASKS[task_id]; t.status="cancelled"; return t
    def list_tasks(self,organization_id=None,workspace_id=None):
        out=list(TASKS.values())
        if organization_id: out=[t for t in out if t.organization_id==organization_id]
        if workspace_id: out=[t for t in out if t.workspace_id==workspace_id]
        return out
queue=WorkerQueue()
