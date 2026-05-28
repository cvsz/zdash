from __future__ import annotations

from collections import deque
from threading import Lock

from app.core.config import get_settings
from app.tenancy.tenant_context import TenantContext
from app.workers.models import WorkerStatus, WorkerTask, now_utc

TASKS: dict[str, WorkerTask] = {}
WORKERS: dict[str, WorkerStatus] = {}
QUEUE: deque[str] = deque()


class WorkerQueue:
    def __init__(self) -> None:
        self._lock = Lock()
        settings = get_settings()
        requested_backend = settings.worker_queue_backend.lower().strip()
        self.backend = "redis" if requested_backend == "redis" else "memory"
        self.using_redis = False
        self.max_retries = settings.worker_max_retries

    def enqueue(
        self,
        task_type: str,
        payload: dict | None,
        tenant_context: TenantContext,
        priority: int = 5,
    ) -> WorkerTask:
        task = WorkerTask(
            organization_id=tenant_context.organization_id,
            workspace_id=tenant_context.workspace_id,
            task_type=task_type,  # type: ignore[arg-type]
            payload=payload or {},
            priority=priority,
            max_retries=self.max_retries,
        )
        with self._lock:
            TASKS[task.id] = task
            QUEUE.append(task.id)
        return task

    def dequeue(self, worker_id: str) -> WorkerTask | None:
        with self._lock:
            if not QUEUE:
                self._touch_worker(worker_id, status="idle")
                return None
            task_id = QUEUE.popleft()
            task = TASKS[task_id]
            task.status = "running"
            task.attempts += 1
            task.started_at = now_utc()
            task.updated_at = now_utc()
            TASKS[task.id] = task
            self._touch_worker(worker_id, status="running", current_task_id=task.id)
            return task

    def complete(self, task_id: str, result: dict) -> WorkerTask:
        with self._lock:
            task = TASKS[task_id]
            task.status = "completed"
            task.result = result
            task.error = None
            task.finished_at = now_utc()
            task.updated_at = now_utc()
            TASKS[task.id] = task
            self._increment_worker_counts(task_id, processed_delta=1)
            return task

    def fail(self, task_id: str, error: str) -> WorkerTask:
        with self._lock:
            task = TASKS[task_id]
            task.status = "failed"
            task.error = error
            task.finished_at = now_utc()
            task.updated_at = now_utc()
            TASKS[task.id] = task
            self._increment_worker_counts(task_id, failed_delta=1)
            return task

    def retry(self, task_id: str) -> WorkerTask:
        with self._lock:
            task = TASKS[task_id]
            if task.attempts >= task.max_retries:
                task.status = "failed"
                task.error = "max retries exceeded"
                task.updated_at = now_utc()
                TASKS[task.id] = task
                return task
            task.status = "retrying"
            task.error = None
            task.updated_at = now_utc()
            TASKS[task.id] = task
            QUEUE.append(task.id)
            return task

    def cancel(self, task_id: str) -> WorkerTask:
        with self._lock:
            task = TASKS[task_id]
            task.status = "cancelled"
            task.updated_at = now_utc()
            task.finished_at = now_utc()
            TASKS[task.id] = task
            try:
                QUEUE.remove(task.id)
            except ValueError:
                pass
            return task

    def get_task(self, task_id: str) -> WorkerTask | None:
        with self._lock:
            return TASKS.get(task_id)

    def list_tasks(
        self,
        organization_id: str | None = None,
        workspace_id: str | None = None,
    ) -> list[WorkerTask]:
        with self._lock:
            items = list(TASKS.values())
        if organization_id:
            items = [task for task in items if task.organization_id == organization_id]
        if workspace_id:
            items = [task for task in items if task.workspace_id == workspace_id]
        return sorted(items, key=lambda task: task.created_at, reverse=True)

    def status_snapshot(self) -> dict:
        with self._lock:
            counts = {
                "queued": len([task for task in TASKS.values() if task.status == "queued"]),
                "running": len([task for task in TASKS.values() if task.status == "running"]),
                "failed": len([task for task in TASKS.values() if task.status == "failed"]),
                "completed": len(
                    [task for task in TASKS.values() if task.status == "completed"]
                ),
            }
            workers = [worker.model_dump() for worker in WORKERS.values()]
        return {
            "backend": self.backend,
            "using_redis": self.using_redis,
            "counts": counts,
            "workers": workers,
        }

    def reset(self) -> None:
        with self._lock:
            TASKS.clear()
            QUEUE.clear()
            WORKERS.clear()

    def _touch_worker(
        self,
        worker_id: str,
        *,
        status: str,
        current_task_id: str | None = None,
    ) -> None:
        worker = WORKERS.get(worker_id)
        if worker is None:
            worker = WorkerStatus(worker_id=worker_id, hostname="local")
        worker.status = status  # type: ignore[assignment]
        worker.current_task_id = current_task_id
        worker.last_heartbeat_at = now_utc()
        WORKERS[worker_id] = worker

    def _increment_worker_counts(
        self,
        task_id: str,
        *,
        processed_delta: int = 0,
        failed_delta: int = 0,
    ) -> None:
        for worker_id, worker in WORKERS.items():
            if worker.current_task_id == task_id:
                worker.processed_count += processed_delta
                worker.failed_count += failed_delta
                worker.current_task_id = None
                worker.status = "idle"
                worker.last_heartbeat_at = now_utc()
                WORKERS[worker_id] = worker
                return


queue = WorkerQueue()
