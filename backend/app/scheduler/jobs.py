from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any
from uuid import uuid4

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import session_scope
from app.core.events import event_bus
from app.models.entities import SchedulerJobRecord
from app.repositories import Repository


@dataclass
class JobRecord:
    id: str
    name: str
    interval_seconds: int
    status: str
    created_at: str


class SchedulerService:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler(timezone='UTC')
        self._job_functions: dict[str, Callable[[], dict[str, Any]]] = {}
        self._lock = Lock()

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def register_job(self, name: str, interval_seconds: int, fn: Callable[[], dict[str, Any]]) -> JobRecord:
        job_id = str(uuid4())
        record = JobRecord(
            id=job_id,
            name=name,
            interval_seconds=interval_seconds,
            status='active',
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._lock:
            self._job_functions[job_id] = fn

        self.scheduler.add_job(self.run_job, 'interval', seconds=interval_seconds, args=[job_id], id=job_id)
        with session_scope() as session:
            Repository(session).upsert_scheduler_job(job_id, name, interval_seconds, 'active')

        event_bus.emit('scheduler_job_created', 'SchedulerService', record.__dict__)
        return record

    def run_job(self, job_id: str) -> dict[str, Any]:
        fn = self._job_functions[job_id]
        result = fn()
        event_bus.emit('scheduler_job_run', 'SchedulerService', {'job_id': job_id, 'result': result})
        return result

    def pause_job(self, job_id: str) -> JobRecord:
        self.scheduler.pause_job(job_id)
        with session_scope() as session:
            repo = Repository(session)
            existing = session.get(SchedulerJobRecord, job_id)
            if existing is not None:
                repo.upsert_scheduler_job(job_id, existing.name, existing.interval_seconds, 'paused')
                record = JobRecord(
                    id=existing.id,
                    name=existing.name,
                    interval_seconds=existing.interval_seconds,
                    status='paused',
                    created_at=existing.created_at.isoformat(),
                )
            else:
                record = JobRecord(id=job_id, name='unknown', interval_seconds=0, status='paused', created_at=datetime.now(timezone.utc).isoformat())
        event_bus.emit('scheduler_job_paused', 'SchedulerService', {'job_id': job_id})
        return record

    def resume_job(self, job_id: str) -> JobRecord:
        self.scheduler.resume_job(job_id)
        with session_scope() as session:
            repo = Repository(session)
            row = session.get(SchedulerJobRecord, job_id)
            if row is not None:
                repo.upsert_scheduler_job(job_id, row.name, row.interval_seconds, 'active')
                record = JobRecord(
                    id=row.id,
                    name=row.name,
                    interval_seconds=row.interval_seconds,
                    status='active',
                    created_at=row.created_at.isoformat(),
                )
            else:
                record = JobRecord(id=job_id, name='unknown', interval_seconds=0, status='active', created_at=datetime.now(timezone.utc).isoformat())
        event_bus.emit('scheduler_job_resumed', 'SchedulerService', {'job_id': job_id})
        return record

    def list_jobs(self) -> list[dict[str, Any]]:
        with session_scope() as session:
            rows = Repository(session).list_scheduler_jobs()
        return [
            {
                'id': r.id,
                'name': r.name,
                'interval_seconds': r.interval_seconds,
                'status': r.status,
                'created_at': r.created_at.isoformat(),
                'updated_at': r.updated_at.isoformat(),
            }
            for r in rows
        ]


scheduler_service = SchedulerService()
