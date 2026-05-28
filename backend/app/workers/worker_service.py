from __future__ import annotations

from app.core.events import event_bus
from app.workers.queue import queue
from .tasks import run_task


def run_once(worker_id: str = "worker-local"):
    task = queue.dequeue(worker_id)
    if not task:
        return None
    try:
        result = run_task(task)
        if result.get("ok"):
            event_bus.emit(
                "worker.task.completed",
                "workers.service",
                f"worker task {task.id} completed",
                {"task_id": task.id, "task_type": task.task_type},
            )
        else:
            event_bus.emit(
                "worker.task.failed",
                "workers.service",
                f"worker task {task.id} failed",
                {"task_id": task.id, "task_type": task.task_type},
            )
        return queue.complete(task.id, result)
    except Exception as exc:
        event_bus.emit(
            "worker.task.failed",
            "workers.service",
            f"worker task {task.id} failed",
            {"task_id": task.id, "task_type": task.task_type, "error": str(exc)},
        )
        return queue.fail(task.id, str(exc))
