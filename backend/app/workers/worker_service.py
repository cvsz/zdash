from .queue import queue
from .tasks import run_task

def run_once(worker_id="worker-local"):
    task=queue.dequeue(worker_id)
    if not task: return None
    try:
        result=run_task(task)
        return queue.complete(task.id,result)
    except Exception as exc:
        return queue.fail(task.id,str(exc))
