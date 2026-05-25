from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.backtesting.backtest_service import backtest_service
from app.backtesting.models import BacktestRequest
from app.content.models import CreateContentRequest
from app.content.pipeline import content_pipeline
from app.core.audit import audit
from app.core.auth import CurrentUser, require_roles
from app.core.observability import scheduler_job_total
from app.core.responses import fail, ok
from app.iot.tapo_adapter import TapoAdapter
from app.scheduler.jobs import scheduler_service
from app.trading.scanner_xau import XAUScanner

router = APIRouter(prefix='/api/scheduler', tags=['scheduler'])

scanner = XAUScanner()
tapo = TapoAdapter()


class JobCreateRequest(BaseModel):
    name: str = Field(min_length=2)
    interval_seconds: int = Field(ge=5)


def _resolve_job(name: str):
    if name == 'trading_scan':
        return lambda: {'signal': scanner.scan().model_dump()}
    if name == 'risk_check':
        return lambda: {'status': 'risk_check_scheduled'}
    if name == 'backtest':
        return lambda: {'result': backtest_service.run_backtest(BacktestRequest(strategy='ob_aggressive', symbol='XAUUSD', timeframe='M5', dataset='mock', initial_balance=10000, risk_per_trade_percent=1, parameters={})).model_dump()}
    if name == 'content_pipeline':
        return lambda: {'pipeline': content_pipeline.run_full_pipeline(CreateContentRequest(topic='zDash weekly system update', content_type='announcement', brand='zDash', language='en', tone='professional', platforms=['x','linkedin'], context={'source':'scheduler','approval_required':True,'dry_run':True})).model_dump()}
    if name == 'health_check':
        return lambda: {'status': 'ok', 'timestamp': datetime.now(timezone.utc).isoformat()}
    if name == 'iot_power_cycle':
        return tapo.power_cycle
    return None


@router.get('/jobs')
def list_jobs(current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst', 'viewer'))):
    return ok({'jobs': scheduler_service.list_jobs()})


@router.post('/jobs')
def create_job(req: JobCreateRequest, current_user: CurrentUser = Depends(require_roles('admin', 'operator'))):
    fn = _resolve_job(req.name)
    if fn is None:
        return fail('UNKNOWN_JOB', f'Unsupported job: {req.name}')
    job = scheduler_service.register_job(req.name, req.interval_seconds, fn)
    scheduler_job_total.labels(action='create').inc()
    audit('scheduler_create_job', current_user.username, current_user.role, target=job.id, detail=req.model_dump())
    return ok({'job': job.__dict__})


@router.post('/jobs/{job_id}/run')
def run_job(job_id: str, current_user: CurrentUser = Depends(require_roles('admin', 'operator'))):
    try:
        result = scheduler_service.run_job(job_id)
    except Exception as exc:
        return fail('JOB_RUN_FAILED', str(exc))
    scheduler_job_total.labels(action='run').inc()
    audit('scheduler_run_job', current_user.username, current_user.role, target=job_id, detail={'result': result})
    return ok({'result': result})


@router.post('/jobs/{job_id}/pause')
def pause_job(job_id: str, current_user: CurrentUser = Depends(require_roles('admin', 'operator'))):
    try:
        job = scheduler_service.pause_job(job_id)
    except Exception as exc:
        return fail('JOB_PAUSE_FAILED', str(exc))
    scheduler_job_total.labels(action='pause').inc()
    audit('scheduler_pause_job', current_user.username, current_user.role, target=job_id)
    return ok({'job': job.__dict__})


@router.post('/jobs/{job_id}/resume')
def resume_job(job_id: str, current_user: CurrentUser = Depends(require_roles('admin', 'operator'))):
    try:
        job = scheduler_service.resume_job(job_id)
    except Exception as exc:
        return fail('JOB_RESUME_FAILED', str(exc))
    scheduler_job_total.labels(action='resume').inc()
    audit('scheduler_resume_job', current_user.username, current_user.role, target=job_id)
    return ok({'job': job.__dict__})


@router.get('/iot/connectivity')
def iot_connectivity(current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst', 'viewer'))):
    return ok({'iot': tapo.connectivity_test()})


@router.post('/iot/power-cycle')
def iot_power_cycle(current_user: CurrentUser = Depends(require_roles('admin', 'operator'))):
    result = tapo.power_cycle()
    audit('iot_power_cycle', current_user.username, current_user.role, detail=result)
    return ok({'result': result})
