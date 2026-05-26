from app.core.events import event_bus
from app.risk.guardian_service import get_guardian_service
from app.scheduler.scheduler_service import get_scheduler_service


def _job_id_by_name(name: str) -> str:
    service = get_scheduler_service()
    for job in service.list_jobs():
        if job.name == name:
            return job.id
    raise AssertionError(f'Missing job: {name}')


def test_risk_check_job_calls_guardian_service() -> None:
    service = get_scheduler_service()
    risk_job_id = _job_id_by_name('risk_check')

    result = service.run_job(risk_job_id)

    assert 'decision' in result.output
    assert result.output['decision']['risk_level'] in {'normal', 'warning', 'danger', 'emergency'}


def test_trading_scan_job_does_not_bypass_halt_flag() -> None:
    service = get_scheduler_service()
    scan_job_id = _job_id_by_name('trading_scan')

    guardian = get_guardian_service()
    guardian.halt('halt for scheduler test', source='manual')

    result = service.run_job(scan_job_id)

    assert result.status in {'blocked_by_risk', 'skipped'}
    assert result.ok is False


def test_scheduler_emits_risk_related_job_output() -> None:
    service = get_scheduler_service()
    scan_job_id = _job_id_by_name('trading_scan')

    guardian = get_guardian_service()
    guardian.halt('halt for event output test', source='manual')

    event_bus.clear()
    service.run_job(scan_job_id)

    events = event_bus.list_events(limit=30)
    scheduler_events = [event for event in events if event.type.startswith('scheduler.job.')]
    assert scheduler_events

    with_output = [event for event in scheduler_events if isinstance(event.payload, dict) and 'output' in event.payload]
    assert with_output
