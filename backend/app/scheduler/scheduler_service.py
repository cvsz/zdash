from __future__ import annotations

from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.core.events import event_bus
from app.scheduler.job_store import InMemoryJobStore, JobNotFoundError
from app.scheduler.jobs import default_jobs, run_scheduled_job
from app.scheduler.models import (
    CreateJobRequest,
    JobRunResult,
    JobStatus,
    ScheduleType,
    ScheduledJob,
)


class SchedulerService:
    def __init__(self, store: InMemoryJobStore | None = None) -> None:
        self.settings = get_settings()
        self.store = store or InMemoryJobStore()
        self.scheduler = BackgroundScheduler(timezone=self.settings.scheduler_timezone)
        self.register_default_jobs()
        event_bus.emit(
            "service.install.script.generated",
            "SchedulerService",
            "NSSM install script is available.",
            {"script": "scripts/install-nssm-service.ps1"},
        )
        event_bus.emit(
            "service.uninstall.script.generated",
            "SchedulerService",
            "NSSM uninstall script is available.",
            {"script": "scripts/uninstall-nssm-service.ps1"},
        )

    def start(self) -> dict:
        if not self.settings.scheduler_enabled:
            return {
                "enabled": False,
                "running": False,
                "message": "Scheduler is disabled by configuration.",
            }

        if not self.scheduler.running:
            self.scheduler.start()
            self._sync_runtime_jobs()
            event_bus.emit(
                "scheduler.started",
                "SchedulerService",
                "Scheduler started",
                {"timezone": self.settings.scheduler_timezone},
            )

        return self.get_status()

    def stop(self) -> dict:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            event_bus.emit(
                "scheduler.stopped", "SchedulerService", "Scheduler stopped", {}
            )
        return self.get_status()

    def get_status(self) -> dict:
        jobs = self.store.list_jobs()
        has_backtest_job = any(job.job_type.value == "backtest" for job in jobs)
        has_content_pipeline_job = any(
            job.job_type.value == "content_pipeline" for job in jobs
        )
        return {
            "enabled": self.settings.scheduler_enabled,
            "running": self.scheduler.running,
            "timezone": self.settings.scheduler_timezone,
            "store": self.settings.scheduler_store,
            "job_count": len(jobs),
            "run_count": len(self.store.list_runs()),
            "backtest_job_registered": has_backtest_job,
            "content_pipeline_job_registered": has_content_pipeline_job,
        }

    def register_default_jobs(self) -> list[ScheduledJob]:
        created: list[ScheduledJob] = []
        existing_names = {job.name for job in self.store.list_jobs()}

        for request in default_jobs():
            if request.name in existing_names:
                continue
            created_job = self.create_job(request)
            created.append(created_job)
            existing_names.add(request.name)

        event_bus.emit(
            "scheduler.default_jobs.registered",
            "SchedulerService",
            "Default scheduler jobs registered",
            {"created_count": len(created), "job_ids": [job.id for job in created]},
        )
        return created

    def list_jobs(self) -> list[ScheduledJob]:
        return self.store.list_jobs()

    def create_job(self, request: CreateJobRequest) -> ScheduledJob:
        job = self.store.create_job(request)
        try:
            self._schedule_job_if_needed(job)
        except Exception:
            self.store.delete_job(job.id)
            raise
        event_bus.emit(
            "scheduler.job.created",
            "SchedulerService",
            "Scheduler job created",
            {"job": job.model_dump(mode="json")},
        )
        return job

    def run_job(self, job_id: str, manual: bool = True) -> JobRunResult:
        job = self.store.get_job(job_id)
        if job is None:
            raise JobNotFoundError(f"Unknown job: {job_id}")

        if not job.enabled:
            return self._record_skipped_run(
                job, "disabled", "Job is disabled and cannot be executed."
            )

        if job.status == JobStatus.paused:
            return self._record_skipped_run(
                job, "skipped", "Job is paused and cannot be executed."
            )

        self.store.update_job(job.id, {"status": JobStatus.running})
        event_bus.emit(
            "scheduler.job.updated",
            "SchedulerService",
            "Scheduler job updated",
            {"job_id": job.id, "status": JobStatus.running.value},
        )
        event_bus.emit(
            "scheduler.job.started",
            "SchedulerService",
            "Scheduler job started",
            {"job_id": job.id, "manual": manual},
        )

        started_at = datetime.now(timezone.utc)
        try:
            ok, status, message, output = run_scheduled_job(job)
        except Exception as exc:
            ok = False
            status = "failed"
            message = f"Scheduler execution failed: {exc}"
            output = {"error": str(exc)}

        finished_at = datetime.now(timezone.utc)
        duration_ms = int((finished_at - started_at).total_seconds() * 1000)

        result = JobRunResult(
            job_id=job.id,
            job_type=job.job_type,
            status=status,
            ok=ok,
            message=message,
            output=output,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=max(0, duration_ms),
        )

        updated_job = self.store.record_run(job.id, result)
        event_bus.emit(
            "scheduler.job.updated",
            "SchedulerService",
            "Scheduler job updated",
            {
                "job_id": job.id,
                "status": updated_job.status.value,
                "run_count": updated_job.run_count,
                "fail_count": updated_job.fail_count,
            },
        )
        self._schedule_job_if_needed(updated_job)

        if result.status in {"skipped", "blocked_by_risk", "disabled", "blocked"}:
            event_bus.emit(
                "scheduler.job.skipped",
                "SchedulerService",
                "Scheduler job skipped",
                {
                    "job_id": job.id,
                    "status": result.status,
                    "message": result.message,
                    "output": result.output,
                },
            )
        elif result.ok:
            event_bus.emit(
                "scheduler.job.completed",
                "SchedulerService",
                "Scheduler job completed",
                {
                    "job_id": job.id,
                    "status": result.status,
                    "message": result.message,
                    "output": result.output,
                },
            )
        else:
            event_bus.emit(
                "scheduler.job.failed",
                "SchedulerService",
                "Scheduler job failed",
                {
                    "job_id": job.id,
                    "status": result.status,
                    "message": result.message,
                    "output": result.output,
                },
            )

        return result

    def pause_job(self, job_id: str) -> ScheduledJob:
        job = self.store.pause_job(job_id)
        runtime_job = self.scheduler.get_job(job_id)
        if runtime_job is not None:
            self.scheduler.pause_job(job_id)
        event_bus.emit(
            "scheduler.job.updated",
            "SchedulerService",
            "Scheduler job updated",
            {"job_id": job_id, "status": job.status.value},
        )
        event_bus.emit(
            "scheduler.job.paused",
            "SchedulerService",
            "Scheduler job paused",
            {"job_id": job_id},
        )
        return job

    def resume_job(self, job_id: str) -> ScheduledJob:
        job = self.store.resume_job(job_id)
        runtime_job = self.scheduler.get_job(job_id)
        if runtime_job is not None:
            self.scheduler.resume_job(job_id)
        else:
            self._schedule_job_if_needed(job)
        event_bus.emit(
            "scheduler.job.updated",
            "SchedulerService",
            "Scheduler job updated",
            {"job_id": job_id, "status": job.status.value},
        )
        event_bus.emit(
            "scheduler.job.resumed",
            "SchedulerService",
            "Scheduler job resumed",
            {"job_id": job_id},
        )
        return job

    def delete_job(self, job_id: str) -> bool:
        runtime_job = self.scheduler.get_job(job_id)
        if runtime_job is not None:
            self.scheduler.remove_job(job_id)

        deleted = self.store.delete_job(job_id)
        if deleted:
            event_bus.emit(
                "scheduler.job.deleted",
                "SchedulerService",
                "Scheduler job deleted",
                {"job_id": job_id},
            )
        return deleted

    def list_runs(self, job_id: str | None = None) -> list[JobRunResult]:
        return self.store.list_runs(job_id=job_id)

    def _record_skipped_run(
        self, job: ScheduledJob, status: str, message: str
    ) -> JobRunResult:
        now = datetime.now(timezone.utc)
        result = JobRunResult(
            job_id=job.id,
            job_type=job.job_type,
            status=status,
            ok=False,
            message=message,
            output={},
            started_at=now,
            finished_at=now,
            duration_ms=0,
        )
        self.store.record_run(job.id, result)
        event_bus.emit(
            "scheduler.job.skipped",
            "SchedulerService",
            "Scheduler job skipped",
            {"job_id": job.id, "status": status, "message": message},
        )
        return result

    def _sync_runtime_jobs(self) -> None:
        for job in self.store.list_jobs():
            self._schedule_job_if_needed(job)

    def _schedule_job_if_needed(self, job: ScheduledJob) -> None:
        should_schedule = (
            job.enabled
            and job.status != JobStatus.paused
            and job.schedule_type
            in {
                ScheduleType.interval,
                ScheduleType.cron,
            }
        )
        if not should_schedule:
            existing = self.scheduler.get_job(job.id)
            if existing is not None:
                self.scheduler.remove_job(job.id)
            return

        if (
            job.schedule_type == ScheduleType.interval
            and job.interval_seconds is not None
        ):
            self.scheduler.add_job(
                self.run_job,
                "interval",
                id=job.id,
                seconds=job.interval_seconds,
                args=[job.id, False],
                replace_existing=True,
                coalesce=True,
                max_instances=1,
                misfire_grace_time=job.max_runtime_seconds,
            )
        elif job.schedule_type == ScheduleType.cron and job.cron:
            trigger = CronTrigger.from_crontab(
                job.cron, timezone=self.settings.scheduler_timezone
            )
            self.scheduler.add_job(
                self.run_job,
                trigger,
                id=job.id,
                args=[job.id, False],
                replace_existing=True,
                coalesce=True,
                max_instances=1,
                misfire_grace_time=job.max_runtime_seconds,
            )

        runtime_job = self.scheduler.get_job(job.id)
        if runtime_job is not None:
            try:
                next_run_at = runtime_job.next_run_time
            except AttributeError:
                next_run_at = None
            self.store.update_job(job.id, {"next_run_at": next_run_at})


_scheduler_service: SchedulerService | None = None


def get_scheduler_service() -> SchedulerService:
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service


def reset_scheduler_service() -> None:
    global _scheduler_service
    if _scheduler_service is not None:
        _scheduler_service.stop()
    _scheduler_service = None
