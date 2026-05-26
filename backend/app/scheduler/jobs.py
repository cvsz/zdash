from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.events import event_bus


def _job_type_value(job_type: Any) -> str:
    return getattr(job_type, 'value', str(job_type))


def _get_guardian_service():
    import app.risk.guardian_service as guardian_module

    if hasattr(guardian_module, 'get_guardian_service'):
        return guardian_module.get_guardian_service()

    if hasattr(guardian_module, 'guardian_service'):
        return guardian_module.guardian_service

    if hasattr(guardian_module, '_guardian_service'):
        return guardian_module._guardian_service

    return None


def _guardian_status() -> Any:
    service = _get_guardian_service()

    if service is None:
        return {
            'halted': False,
            'kill_switch_active': False,
            'blocked': False,
            'available': False,
            'reason': 'guardian_service_unavailable',
        }

    if hasattr(service, 'get_status'):
        return service.get_status()

    if hasattr(service, 'status'):
        value = service.status
        return value() if callable(value) else value

    return {
        'halted': False,
        'kill_switch_active': False,
        'blocked': False,
        'available': False,
        'reason': 'guardian_status_unavailable',
    }


def _status_to_dict(status: Any) -> dict[str, Any]:
    if isinstance(status, dict):
        return status

    if hasattr(status, 'model_dump'):
        return status.model_dump(mode='json')

    if hasattr(status, 'dict'):
        return status.dict()

    return {
        'halted': bool(getattr(status, 'halted', False)),
        'kill_switch_active': bool(getattr(status, 'kill_switch_active', False)),
        'blocked': bool(getattr(status, 'blocked', False)),
        'raw': str(status),
    }


def _status_is_blocked(status: Any) -> bool:
    if isinstance(status, dict):
        halt_state = status.get('halt_state') or {}
        return bool(
            status.get('halted')
            or status.get('kill_switch_active')
            or status.get('blocked')
            or halt_state.get('halted')
        )

    halt_state = getattr(status, 'halt_state', None)
    nested_halted = False
    if isinstance(halt_state, dict):
        nested_halted = bool(halt_state.get('halted'))
    elif halt_state is not None:
        nested_halted = bool(getattr(halt_state, 'halted', False))

    return bool(
        getattr(status, 'halted', False)
        or getattr(status, 'kill_switch_active', False)
        or getattr(status, 'blocked', False)
        or nested_halted
    )


def _risk_level(status: Any) -> str:
    status_dict = _status_to_dict(status)
    raw = (
        status_dict.get('risk_level')
        or status_dict.get('current_risk_status')
        or status_dict.get('status')
        or 'normal'
    )
    value = str(raw).lower()

    if value in {'normal', 'warning', 'danger', 'emergency'}:
        return value

    if status_dict.get('kill_switch_active'):
        return 'emergency'

    halt_state = status_dict.get('halt_state') or {}
    if status_dict.get('halted') or halt_state.get('halted') or status_dict.get('blocked'):
        return 'danger'

    return 'normal'


def default_jobs():
    """Default safe scheduler jobs.

    Must stay callable because scheduler_service.py calls default_jobs().
    Job names are test/runtime contract values.
    """
    from app.scheduler.models import CreateJobRequest, JobType, ScheduleType

    return [
        CreateJobRequest(
            name='health_check',
            job_type=JobType.health_check,
            schedule_type=ScheduleType.interval,
            interval_seconds=300,
            payload={'dry_run': True},
            enabled=True,
        ),
        CreateJobRequest(
            name='risk_check',
            job_type=JobType.risk_check,
            schedule_type=ScheduleType.interval,
            interval_seconds=300,
            payload={'dry_run': True},
            enabled=True,
        ),
        CreateJobRequest(
            name='trading_scan',
            job_type=JobType.trading_scan,
            schedule_type=ScheduleType.interval,
            interval_seconds=300,
            payload={'symbol': 'XAUUSD', 'timeframe': 'M5', 'dry_run': True},
            enabled=True,
        ),
        CreateJobRequest(
            name='iot_power_cycle',
            job_type=JobType.iot_power_cycle,
            schedule_type=ScheduleType.manual,
            payload={'dry_run': True, 'requires_confirmation': True},
            enabled=False,
        ),
    ]


def run_scheduled_job(job):
    """Run one scheduled job in safe dry-run mode.

    Contract expected by scheduler_service.py:
        ok, status, message, output = run_scheduled_job(job)
    """
    job_id = getattr(job, 'id', 'unknown')
    job_type = _job_type_value(getattr(job, 'job_type', 'custom'))
    payload = getattr(job, 'payload', {}) or {}

    if job_type == 'health_check':
        ok = True
        status = 'completed'
        message = 'health check completed'
        output = {
            'ok': True,
            'job_id': str(job_id),
            'job_type': job_type,
            'mode': 'dry_run',
            'status': 'healthy',
        }

    elif job_type == 'risk_check':
        guardian_status = _guardian_status()
        guardian_dict = _status_to_dict(guardian_status)
        blocked = _status_is_blocked(guardian_status)

        ok = True
        status = 'completed'
        message = 'risk check completed'
        output = {
            'ok': True,
            'job_id': str(job_id),
            'job_type': job_type,
            'mode': 'dry_run',
            'risk_status': guardian_dict,
            'decision': {
                'allowed': not blocked,
                'blocked': blocked,
                'risk_level': _risk_level(guardian_status),
                'reason': 'guardian_halted_or_kill_switch' if blocked else 'risk_check_passed',
            },
        }

    elif job_type == 'trading_scan':
        guardian_status = _guardian_status()
        guardian_dict = _status_to_dict(guardian_status)
        blocked = _status_is_blocked(guardian_status)

        ok = not blocked
        status = 'blocked_by_risk' if blocked else 'completed'
        message = 'trading scan blocked by risk' if blocked else 'trading scan dry-run completed'
        output = {
            'ok': not blocked,
            'job_id': str(job_id),
            'job_type': job_type,
            'mode': 'dry_run',
            'blocked_by_risk': blocked,
            'risk_status': guardian_dict,
            'symbol': payload.get('symbol', 'XAUUSD'),
            'timeframe': payload.get('timeframe', 'M5'),
        }

    elif job_type == 'iot_power_cycle':
        ok = True
        status = 'skipped'
        message = 'iot power cycle skipped in dry-run mode'
        output = {
            'ok': True,
            'job_id': str(job_id),
            'job_type': job_type,
            'mode': 'dry_run',
            'action': 'iot_power_cycle',
            'allowed': False,
            'requires_confirmation': True,
            'reason': 'iot actions remain dry-run/confirmation-gated by default',
        }

    else:
        if payload.get('force_fail') is True:
            ok = False
            status = 'failed'
            message = 'custom job forced failure'
            output = {
                'ok': False,
                'job_id': str(job_id),
                'job_type': job_type,
                'mode': 'dry_run',
                'error': 'forced_failure',
                'payload': payload,
            }
        else:
            ok = True
            status = 'completed'
            message = 'custom job dry-run completed'
            output = {
                'ok': True,
                'job_id': str(job_id),
                'job_type': job_type,
                'mode': 'dry_run',
                'payload': payload,
            }

    event_bus.emit(
        'scheduler_job_dry_run',
        'SchedulerService',
        message,
        {
            'job_id': str(job_id),
            'job_type': job_type,
            'status': status,
            'ok': ok,
            'output': output,
        },
    )

    return ok, status, message, output

