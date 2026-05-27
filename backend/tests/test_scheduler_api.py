from app.api import scheduler
from app.scheduler.models import CreateJobRequest, JobType, ScheduleType


def _assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {"ok", "data", "error", "timestamp"}


def test_get_scheduler_status() -> None:
    body = scheduler.status()
    _assert_envelope(body)
    assert "scheduler" in body["data"]


def test_get_scheduler_jobs() -> None:
    body = scheduler.list_jobs()
    _assert_envelope(body)
    assert "jobs" in body["data"]


def test_post_scheduler_jobs() -> None:
    req = CreateJobRequest(
        name="Manual XAU scan",
        job_type=JobType.trading_scan,
        schedule_type=ScheduleType.manual,
        payload={"symbol": "XAUUSD", "timeframe": "M5", "dry_run": True},
        enabled=True,
    )
    body = scheduler.create_job(req)
    _assert_envelope(body)
    assert body["ok"] is True
    assert body["data"]["job"]["name"] == "Manual XAU scan"


def test_post_scheduler_run_pause_resume_delete() -> None:
    req = CreateJobRequest(
        name="Manual health",
        job_type=JobType.health_check,
        schedule_type=ScheduleType.manual,
        payload={},
        enabled=True,
    )
    created = scheduler.create_job(req)
    job_id = created["data"]["job"]["id"]

    run_body = scheduler.run_job(job_id)
    pause_body = scheduler.pause_job(job_id)
    resume_body = scheduler.resume_job(job_id)
    delete_body = scheduler.delete_job(job_id)

    for payload in (run_body, pause_body, resume_body, delete_body):
        _assert_envelope(payload)
        assert payload["ok"] is True


def test_get_scheduler_runs() -> None:
    body = scheduler.list_runs()
    _assert_envelope(body)
    assert "runs" in body["data"]


def test_get_scheduler_runs_for_job() -> None:
    req = CreateJobRequest(
        name="runs-target",
        job_type=JobType.health_check,
        schedule_type=ScheduleType.manual,
        payload={},
        enabled=True,
    )
    created = scheduler.create_job(req)
    job_id = created["data"]["job"]["id"]
    scheduler.run_job(job_id)

    body = scheduler.list_runs_for_job(job_id)
    _assert_envelope(body)
    assert body["data"]["job_id"] == job_id
