import pytest

from app.scheduler.models import CreateJobRequest, JobStatus, JobType, ScheduleType


def test_valid_interval_job() -> None:
    req = CreateJobRequest(
        name="health poll",
        job_type=JobType.health_check,
        schedule_type=ScheduleType.interval,
        interval_seconds=60,
    )
    assert req.interval_seconds == 60


def test_invalid_interval_job_rejects_missing_interval_seconds() -> None:
    with pytest.raises(ValueError):
        CreateJobRequest(
            name="broken interval",
            job_type=JobType.health_check,
            schedule_type=ScheduleType.interval,
            interval_seconds=None,
        )


def test_cron_job_requires_cron_string() -> None:
    with pytest.raises(ValueError):
        CreateJobRequest(
            name="broken cron",
            job_type=JobType.health_check,
            schedule_type=ScheduleType.cron,
            cron="",
        )


def test_manual_job_accepts_no_schedule() -> None:
    req = CreateJobRequest(
        name="manual scan",
        job_type=JobType.trading_scan,
        schedule_type=ScheduleType.manual,
    )
    assert req.cron is None
    assert req.interval_seconds is None


def test_status_enum_values() -> None:
    values = {status.value for status in JobStatus}
    assert values == {"pending", "running", "paused", "completed", "failed", "disabled"}
