from app.core.config import get_settings
from app.risk.guardian_service import get_guardian_service, reset_guardian_service
from app.risk.models import AccountSnapshot
from app.trading.execution_engine import ExecutionEngine
from app.trading.risk_models import ExecutionRequest, Signal


def _safe_snapshot() -> AccountSnapshot:
    return AccountSnapshot(
        balance=10000.0,
        equity=10000.0,
        peak_equity=10000.0,
        daily_start_equity=10000.0,
        open_positions=0,
        floating_pnl=0.0,
        realized_pnl_today=0.0,
    )


def _breached_snapshot() -> AccountSnapshot:
    return AccountSnapshot(
        balance=10000.0,
        equity=7000.0,
        peak_equity=10000.0,
        daily_start_equity=10000.0,
        open_positions=0,
        floating_pnl=-3000.0,
        realized_pnl_today=-3000.0,
    )


def _signal() -> Signal:
    return Signal(
        symbol='XAUUSD',
        timeframe='M5',
        direction='buy',
        strategy='ob_aggressive',
        confidence=0.72,
    )


def test_execution_blocked_when_halt_active() -> None:
    get_settings.cache_clear()
    reset_guardian_service()
    service = get_guardian_service()
    service.halt('Manual halt', source='manual')

    engine = ExecutionEngine()
    result = engine.execute(ExecutionRequest(signal=_signal(), snapshot=_safe_snapshot()))

    assert result.status == 'blocked_by_risk'


def test_execution_blocked_when_drawdown_breached() -> None:
    get_settings.cache_clear()
    reset_guardian_service()
    engine = ExecutionEngine()

    result = engine.execute(ExecutionRequest(signal=_signal(), snapshot=_breached_snapshot()))
    assert result.status == 'blocked_by_risk'


def test_dry_run_execution_allowed_when_risk_normal() -> None:
    get_settings.cache_clear()
    reset_guardian_service()
    engine = ExecutionEngine()

    result = engine.execute(ExecutionRequest(signal=_signal(), snapshot=_safe_snapshot()))
    assert result.status == 'simulated'
    assert result.dry_run is True


def test_live_execution_blocked_unless_live_trading_ack(monkeypatch) -> None:
    monkeypatch.setenv('DRY_RUN', 'false')
    monkeypatch.setenv('LIVE_TRADING_ACK', 'false')
    monkeypatch.setenv('RISK_GUARDIAN_ENABLED', 'true')
    get_settings.cache_clear()
    reset_guardian_service()

    engine = ExecutionEngine()
    result = engine.execute(
        ExecutionRequest(signal=_signal(), snapshot=_safe_snapshot(), dry_run=False, confirmation=True)
    )

    assert result.status == 'blocked_by_config'

    get_settings.cache_clear()
    reset_guardian_service()
