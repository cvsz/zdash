from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.audit import audit
from app.core.auth import CurrentUser, require_roles
from app.core.config import get_settings
from app.core.database import session_scope
from app.core.events import event_bus
from app.core.observability import risk_halt_total
from app.core.responses import fail, ok
from app.repositories import Repository
from app.risk.drawdown_guard import DrawdownGuard, EquitySnapshot
from app.risk.halt_flag import clear_halt, get_halt_state, set_halt
from app.risk.kill_switch import KillSwitch

router = APIRouter(prefix='/api/risk', tags=['risk'])
settings = get_settings()
drawdown_guard = DrawdownGuard()
kill_switch = KillSwitch()

DEFAULT_RISK_STORE = {
    'start_balance': 10000.0,
    'current_balance': 10000.0,
    'peak_balance': 10000.0,
    'updated_at': datetime.now(timezone.utc).isoformat(),
}


class HaltRequest(BaseModel):
    reason: str = Field(min_length=3)


class RiskCheckRequest(BaseModel):
    current_balance: float


def _load_risk_store() -> dict:
    with session_scope() as session:
        decision = Repository(session).latest_risk_decision('equity_state')
    if decision and isinstance(decision.payload, dict):
        return decision.payload
    return dict(DEFAULT_RISK_STORE)


def _save_risk_store(payload: dict) -> None:
    with session_scope() as session:
        Repository(session).add_risk_decision('equity_state', 'equity snapshot update', payload, immutable=True)


@router.get('/status')
def risk_status(current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst', 'viewer'))):
    return ok({'halt': get_halt_state().__dict__, 'risk_store': _load_risk_store()})


@router.post('/halt')
def halt(req: HaltRequest, current_user: CurrentUser = Depends(require_roles('admin', 'operator'))):
    state = set_halt(req.reason, actor=current_user.username)
    risk_halt_total.labels(type='manual').inc()
    with session_scope() as session:
        Repository(session).add_risk_decision('manual_halt', req.reason, {'state': state.__dict__}, immutable=True)
    event_bus.emit('risk_halt', 'RiskAPI', {'action': 'halt', 'reason': req.reason})
    audit('risk_halt', current_user.username, current_user.role, detail={'reason': req.reason})
    return ok({'halt': state.__dict__})


@router.post('/emergency-halt')
def emergency_halt(req: HaltRequest, current_user: CurrentUser = Depends(require_roles('admin'))):
    state = set_halt(req.reason, actor=current_user.username, locked=True)
    risk_halt_total.labels(type='emergency').inc()
    with session_scope() as session:
        Repository(session).add_risk_decision('emergency_halt', req.reason, {'state': state.__dict__}, immutable=True)
    event_bus.emit('risk_halt', 'RiskAPI', {'action': 'emergency_halt', 'reason': req.reason})
    audit('risk_emergency_halt', current_user.username, current_user.role, detail={'reason': req.reason})
    return ok({'halt': state.__dict__})


@router.post('/resume')
def resume(req: HaltRequest, current_user: CurrentUser = Depends(require_roles('admin'))):
    current = get_halt_state()
    if current.locked:
        return fail('HALT_LOCKED', 'Emergency halt is locked. Use kill-switch reset endpoint.')
    state = clear_halt(req.reason, actor=current_user.username)
    with session_scope() as session:
        Repository(session).add_risk_decision('resume', req.reason, {'state': state.__dict__}, immutable=True)
    event_bus.emit('risk_halt', 'RiskAPI', {'action': 'resume', 'reason': req.reason})
    audit('risk_resume', current_user.username, current_user.role, detail={'reason': req.reason})
    return ok({'halt': state.__dict__})


@router.post('/kill-switch-reset')
def kill_switch_reset(req: HaltRequest, current_user: CurrentUser = Depends(require_roles('admin'))):
    state = set_halt('kill switch reset requested by admin', actor=current_user.username, locked=False)
    state = clear_halt(req.reason, actor=current_user.username)
    with session_scope() as session:
        Repository(session).add_risk_decision('kill_switch_reset', req.reason, {'state': state.__dict__}, immutable=True)
    audit('kill_switch_reset', current_user.username, current_user.role, detail={'reason': req.reason})
    return ok({'halt': state.__dict__})


@router.post('/check')
def risk_check(req: RiskCheckRequest, current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst'))):
    risk_store = _load_risk_store()
    risk_store['current_balance'] = req.current_balance
    risk_store['peak_balance'] = max(risk_store['peak_balance'], req.current_balance)
    risk_store['updated_at'] = datetime.now(timezone.utc).isoformat()
    _save_risk_store(risk_store)

    snapshot = EquitySnapshot(
        start_balance=risk_store['start_balance'],
        current_balance=risk_store['current_balance'],
        peak_balance=risk_store['peak_balance'],
    )
    dds = drawdown_guard.evaluate(snapshot)
    kill = kill_switch.check(dds['total_drawdown_percent'])

    daily_limit_hit = dds['daily_drawdown_percent'] >= settings.max_daily_drawdown_percent
    total_limit_hit = dds['total_drawdown_percent'] >= settings.max_total_drawdown_percent

    if kill['emergency_triggered']:
        state = set_halt('Emergency kill switch triggered', actor='system', locked=True)
        risk_halt_total.labels(type='auto_emergency').inc()
    elif daily_limit_hit or total_limit_hit:
        state = set_halt('Drawdown threshold reached', actor='system')
        risk_halt_total.labels(type='auto_threshold').inc()
    else:
        state = get_halt_state()

    with session_scope() as session:
        Repository(session).add_risk_decision('risk_check', 'risk check evaluated', {'drawdown': dds, 'kill': kill, 'halt': state.__dict__}, immutable=True)

    event_bus.emit('risk_check', 'RiskAPI', {'drawdown': dds, 'kill': kill, 'halt': state.__dict__})
    return ok({'drawdown': dds, 'kill_switch': kill, 'halt': state.__dict__})


@router.get('/drawdown')
def get_drawdown(current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst', 'viewer'))):
    risk_store = _load_risk_store()
    snapshot = EquitySnapshot(
        start_balance=risk_store['start_balance'],
        current_balance=risk_store['current_balance'],
        peak_balance=risk_store['peak_balance'],
    )
    return ok({'drawdown': drawdown_guard.evaluate(snapshot)})
