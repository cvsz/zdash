from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.scheduler.job_store import InMemoryJobStore
from app.scheduler.models import JobStatus, JobType, ScheduledJob, ScheduleType


class SchedulerServiceV2:
    def __init__(self, store: InMemoryJobStore | None = None) -> None:
        self.store = store or InMemoryJobStore()

    def create_job(self, name: str, job_type: JobType, schedule_type: ScheduleType, **kwargs) -> ScheduledJob:
        now = datetime.now(timezone.utc)
        job = ScheduledJob(
            id=str(uuid4()),
            name=name,
            job_type=job_type,
            schedule_type=schedule_type,
            created_at=now,
            updated_at=now,
            interval_seconds=kwargs.get('interval_seconds'),
            cron=kwargs.get('cron'),
            payload=kwargs.get('payload', {}),
            max_runtime_seconds=kwargs.get('max_runtime_seconds', 300),
        )
        return self.store.upsert(job)

    def pause_job(self, job_id: str) -> ScheduledJob:
        job = self._require_job(job_id)
        job.status = JobStatus.paused
        job.updated_at = datetime.now(timezone.utc)
        return self.store.upsert(job)

    def resume_job(self, job_id: str) -> ScheduledJob:
        job = self._require_job(job_id)
        job.status = JobStatus.pending
        job.updated_at = datetime.now(timezone.utc)
        return self.store.upsert(job)

    def delete_job(self, job_id: str) -> None:
        self.store.delete(job_id)

    def list_jobs(self) -> list[ScheduledJob]:
        return self.store.list()

    def _require_job(self, job_id: str) -> ScheduledJob:
        job = self.store.get(job_id)
        if job is None:
            raise ValueError(f'Unknown job: {job_id}')
        return job
