from __future__ import annotations

from datetime import datetime, timedelta, timezone
from threading import Lock
from uuid import uuid4

from app.scheduler.models import CreateJobRequest, JobRunResult, JobStatus, ScheduleType, ScheduledJob


class JobStoreError(ValueError):
    """Base domain error for scheduler store operations."""


class JobNotFoundError(JobStoreError):
    pass


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, ScheduledJob] = {}
        self._runs: list[JobRunResult] = []
        self._lock = Lock()

    @staticmethod
    def _next_run_at(schedule_type: ScheduleType, interval_seconds: int | None) -> datetime | None:
        if schedule_type == ScheduleType.interval and interval_seconds:
            return datetime.now(timezone.utc) + timedelta(seconds=interval_seconds)
        return None

    def list_jobs(self) -> list[ScheduledJob]:
        with self._lock:
            return [job.model_copy(deep=True) for job in self._jobs.values()]

    def get_job(self, job_id: str) -> ScheduledJob | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return job.model_copy(deep=True) if job is not None else None

    def create_job(self, request: CreateJobRequest) -> ScheduledJob:
        now = datetime.now(timezone.utc)
        job = ScheduledJob(
            id=str(uuid4()),
            name=request.name,
            job_type=request.job_type,
            schedule_type=request.schedule_type,
            status=JobStatus.pending if request.enabled else JobStatus.disabled,
            enabled=request.enabled,
            cron=request.cron,
            interval_seconds=request.interval_seconds,
            payload=request.payload,
            max_runtime_seconds=request.max_runtime_seconds,
            created_at=now,
            updated_at=now,
            next_run_at=self._next_run_at(request.schedule_type, request.interval_seconds),
        )
        with self._lock:
            self._jobs[job.id] = job
        return job.model_copy(deep=True)

    def update_job(self, job_id: str, patch: dict) -> ScheduledJob:
        with self._lock:
            current = self._jobs.get(job_id)
            if current is None:
                raise JobNotFoundError(f'Unknown job: {job_id}')

            merged = current.model_dump()
            merged.update(patch)
            merged['updated_at'] = datetime.now(timezone.utc)
            updated = ScheduledJob.model_validate(merged)
            self._jobs[job_id] = updated
            return updated.model_copy(deep=True)

    def delete_job(self, job_id: str) -> bool:
        with self._lock:
            existed = job_id in self._jobs
            if existed:
                del self._jobs[job_id]
            return existed

    def pause_job(self, job_id: str) -> ScheduledJob:
        return self.update_job(job_id, {'status': JobStatus.paused})

    def resume_job(self, job_id: str) -> ScheduledJob:
        current = self.get_job(job_id)
        if current is None:
            raise JobNotFoundError(f'Unknown job: {job_id}')
        status = JobStatus.pending if current.enabled else JobStatus.disabled
        patch = {
            'status': status,
            'next_run_at': self._next_run_at(current.schedule_type, current.interval_seconds),
        }
        return self.update_job(job_id, patch)

    def record_run(self, job_id: str, result: JobRunResult) -> ScheduledJob:
        with self._lock:
            current = self._jobs.get(job_id)
            if current is None:
                raise JobNotFoundError(f'Unknown job: {job_id}')

            self._runs.append(result.model_copy(deep=True))

            run_count = current.run_count + 1
            fail_count = current.fail_count + (0 if result.ok else 1)
            if current.status == JobStatus.paused:
                status = JobStatus.paused
            elif not current.enabled:
                status = JobStatus.disabled
            elif result.status == 'failed':
                status = JobStatus.failed
            elif current.schedule_type in {ScheduleType.interval, ScheduleType.cron}:
                status = JobStatus.pending
            else:
                status = JobStatus.completed if result.ok else JobStatus.failed

            updated = current.model_copy(
                update={
                    'status': status,
                    'last_run_at': result.finished_at,
                    'run_count': run_count,
                    'fail_count': fail_count,
                    'updated_at': datetime.now(timezone.utc),
                    'next_run_at': self._next_run_at(current.schedule_type, current.interval_seconds),
                }
            )
            self._jobs[job_id] = updated
            return updated.model_copy(deep=True)

    def list_runs(self, job_id: str | None = None) -> list[JobRunResult]:
        with self._lock:
            runs = self._runs
            if job_id is not None:
                runs = [item for item in runs if item.job_id == job_id]
            return [item.model_copy(deep=True) for item in runs]
