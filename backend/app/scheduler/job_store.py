from __future__ import annotations

from threading import Lock

from app.scheduler.models import ScheduledJob


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, ScheduledJob] = {}
        self._lock = Lock()

    def upsert(self, job: ScheduledJob) -> ScheduledJob:
        with self._lock:
            self._jobs[job.id] = job
            return job

    def get(self, job_id: str) -> ScheduledJob | None:
        return self._jobs.get(job_id)

    def delete(self, job_id: str) -> None:
        with self._lock:
            self._jobs.pop(job_id, None)

    def list(self) -> list[ScheduledJob]:
        return list(self._jobs.values())
