from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.ai.claude_adapter import ClaudeAdapter
from app.core.audit import audit
from app.core.auth import CurrentUser, get_current_user, require_roles
from app.core.database import get_session, session_scope
from app.core.events import event_bus
from app.core.observability import execution_blocked_total, signal_validation_total, trading_scan_total
from app.core.responses import fail, ok
from app.repositories import Repository
from app.trading.execution_engine import ExecutionEngine
from app.trading.mt5_adapter import MT5Adapter
from app.trading.risk_models import ExecutionRequest, Signal
from app.trading.scanner_xau import XAUScanner
from app.trading.signal_validator import SignalValidator

router = APIRouter(prefix='/api/trading', tags=['trading'])

mt5 = MT5Adapter()
scanner = XAUScanner(mt5=mt5)
validator = SignalValidator()
executor = ExecutionEngine()
ai_adapter = ClaudeAdapter()


class AnalyzeRequest(BaseModel):
    text: str


class ExecutionPayload(BaseModel):
    signal: dict
    lot_size: float = 0.01


class LiveModeConfirmRequest(BaseModel):
    approved: bool
    reason: str = Field(min_length=3)


@router.get('/status')
def trading_status():
    return ok({'mt5': mt5.status()})


@router.get('/live-gates')
def live_gates(current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst', 'viewer'))):
    settings = mt5.settings
    with session_scope() as session:
        approval = Repository(session).latest_live_mode_approval()
    gates = {
        'dry_run_false': not settings.dry_run,
        'live_trading_ack': settings.live_trading_ack,
        'risk_guardian_enabled': settings.risk_guardian_enabled,
        'admin_approved_live_mode': settings.admin_approved_live_mode,
        'latest_manual_approval': bool(approval and approval.approved),
    }
    gates['all_enabled'] = all(gates.values())
    return ok({'gates': gates})


@router.get('/mt5/diagnostics')
def mt5_diagnostics(current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst', 'viewer'))):
    return ok({'diagnostics': mt5.diagnostics()})


@router.get('/mt5/symbol/{symbol}')
def mt5_symbol_check(symbol: str, current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst', 'viewer'))):
    return ok({'symbol': symbol, 'available': mt5.symbol_available(symbol)})


@router.post('/scan')
def scan_signal(current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst', 'viewer'))):
    signal = scanner.scan()
    trading_scan_total.inc()
    payload = signal.model_dump()
    event_bus.emit('trading_signal', 'XAUScanner', payload)
    with session_scope() as session:
        Repository(session).add_trading_signal(payload)
    return ok({'signal': payload})


@router.post('/analyze')
async def analyze(req: AnalyzeRequest, current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst', 'viewer'))):
    summary = await ai_adapter.analyze(req.text)
    event_bus.emit('ai_decision', 'ClaudeAdapter', {'prompt': req.text, 'summary': summary})
    return ok({'summary': summary})


@router.post('/validate-signal')
def validate_signal(req: ExecutionPayload, current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst', 'viewer'))):
    try:
        signal = Signal.model_validate(req.signal)
    except Exception:
        return fail('INVALID_SIGNAL', 'Unable to parse signal payload')
    validation = validator.validate(signal)
    signal_validation_total.labels(valid=str(validation['valid']).lower()).inc()
    return ok({'validation': validation})


@router.post('/dry-run')
def dry_run(req: ExecutionPayload, current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst'))):
    try:
        signal = Signal.model_validate(req.signal)
    except Exception:
        return fail('INVALID_SIGNAL', 'Unable to parse signal payload')

    validation = validator.validate(signal)
    signal_validation_total.labels(valid=str(validation['valid']).lower()).inc()
    if not validation['valid']:
        return fail('SIGNAL_VALIDATION_FAILED', ', '.join(validation['issues']))

    result = executor.execute(ExecutionRequest(signal=signal, lot_size=req.lot_size))
    if result.get('mode') == 'blocked':
        execution_blocked_total.inc()
    event_bus.emit('execution_attempt', 'ExecutionEngine', result)
    with session_scope() as session:
        Repository(session).add_execution_attempt(result)
    return ok({'execution': result, 'validation': validation})


@router.post('/live-mode/confirm')
def confirm_live_mode(
    req: LiveModeConfirmRequest,
    current_user: CurrentUser = Depends(require_roles('admin')),
):
    with session_scope() as session:
        Repository(session).add_live_mode_approval(
            actor=current_user.username,
            approved=req.approved,
            reason=req.reason,
        )
    audit('live_mode_confirm', current_user.username, current_user.role, detail=req.model_dump())
    return ok({'approved': req.approved, 'reason': req.reason})


@router.post('/live-execute')
def live_execute(
    req: ExecutionPayload,
    current_user: CurrentUser = Depends(require_roles('admin', 'operator')),
):
    try:
        signal = Signal.model_validate(req.signal)
    except Exception:
        return fail('INVALID_SIGNAL', 'Unable to parse signal payload')

    validation = validator.validate(signal)
    signal_validation_total.labels(valid=str(validation['valid']).lower()).inc()
    if not validation['valid']:
        return fail('SIGNAL_VALIDATION_FAILED', ', '.join(validation['issues']))

    result = executor.execute(ExecutionRequest(signal=signal, lot_size=req.lot_size))
    if result.get('mode') == 'blocked':
        execution_blocked_total.inc()
    with session_scope() as session:
        Repository(session).add_execution_attempt(result)
    audit('live_execute', current_user.username, current_user.role, detail={'result': result})
    if result.get('mode') != 'live':
        return fail('LIVE_GATES_NOT_SATISFIED', result.get('reason', 'Live gates not satisfied'))
    return ok({'execution': result, 'validation': validation})
