from app.scheduler.models import CreateJobRequest, JobType, ScheduleType
from app.scheduler.scheduler_service import get_scheduler_service


def _find_job_id_by_name(name: str) -> str:
    for job in get_scheduler_service().list_jobs():
        if job.name == name:
            return job.id
    raise AssertionError(f'job not found: {name}')


def test_register_default_jobs() -> None:
    service = get_scheduler_service()
    names = {job.name for job in service.list_jobs()}
    assert 'health_check' in names
    assert 'risk_check' in names
    assert 'trading_scan' in names
    assert 'iot_power_cycle' in names


def test_create_custom_job() -> None:
    service = get_scheduler_service()
    job = service.create_job(
        CreateJobRequest(
            name='custom cron',
            job_type=JobType.custom,
            schedule_type=ScheduleType.cron,
            cron='*/5 * * * *',
            payload={'hello': 'world'},
        )
    )
    assert job.name == 'custom cron'
    assert job.schedule_type == ScheduleType.cron


def test_list_jobs() -> None:
    service = get_scheduler_service()
    jobs = service.list_jobs()
    assert len(jobs) >= 1


def test_pause_job() -> None:
    service = get_scheduler_service()
    job_id = _find_job_id_by_name('health_check')
    job = service.pause_job(job_id)
    assert job.status.value == 'paused'


def test_resume_job() -> None:
    service = get_scheduler_service()
    job_id = _find_job_id_by_name('health_check')
    service.pause_job(job_id)
    job = service.resume_job(job_id)
    assert job.status.value == 'pending'


def test_delete_job() -> None:
    service = get_scheduler_service()
    created = service.create_job(
        CreateJobRequest(
            name='to-delete',
            job_type=JobType.custom,
            schedule_type=ScheduleType.manual,
        )
    )
    assert service.delete_job(created.id) is True


def test_run_health_check_job() -> None:
    service = get_scheduler_service()
    job_id = _find_job_id_by_name('health_check')
    result = service.run_job(job_id)
    assert result.ok is True
    assert result.status == 'completed'


def test_failed_job_is_captured_as_job_run_result() -> None:
    service = get_scheduler_service()
    created = service.create_job(
        CreateJobRequest(
            name='force-fail',
            job_type=JobType.custom,
            schedule_type=ScheduleType.manual,
            payload={'force_fail': True},
        )
    )
    result = service.run_job(created.id)
    assert result.ok is False
    assert result.status == 'failed'

    runs = service.list_runs(created.id)
    assert len(runs) == 1
    assert runs[0].status == 'failed'
