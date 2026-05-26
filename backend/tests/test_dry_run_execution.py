from app.core.config import get_settings
from app.risk.guardian_service import reset_guardian_service
from app.trading.execution_engine import ExecutionEngine
from app.trading.models import ExecutionRequest, TradingSignal


def _signal() -> TradingSignal:
    return TradingSignal(
        symbol='XAUUSD',
        timeframe='M5',
        direction='buy',
        strategy='ob_aggressive',
        confidence=0.73,
        entry=2300.0,
        stop_loss=2298.0,
        take_profit=2304.0,
        reason='execution test',
    )


def test_dry_run_execution_simulates() -> None:
    reset_guardian_service()
    engine = ExecutionEngine()
    result = engine.execute(ExecutionRequest(signal=_signal(), dry_run=True, confirmation=False))

    assert result.ok is True
    assert result.status == 'simulated'
    assert result.dry_run is True
    assert result.simulated_order_id is not None
    assert result.risk_decision is not None
    assert result.risk_decision.approved is True


def test_live_execution_blocked_by_config(monkeypatch) -> None:
    monkeypatch.setenv('DRY_RUN', 'false')
    monkeypatch.setenv('LIVE_TRADING_ACK', 'false')
    get_settings.cache_clear()
    reset_guardian_service()

    engine = ExecutionEngine()
    result = engine.execute(ExecutionRequest(signal=_signal(), dry_run=False, confirmation=True))

    assert result.ok is False
    assert result.status == 'blocked_by_config'
    assert result.risk_decision is not None
    assert result.risk_decision.approved is True

    get_settings.cache_clear()
    reset_guardian_service()


def test_invalid_signal_blocked() -> None:
    reset_guardian_service()
    engine = ExecutionEngine()
    bad_signal = _signal().model_copy(update={'stop_loss': 2302.0, 'take_profit': 2299.0})
    result = engine.execute(ExecutionRequest(signal=bad_signal, dry_run=True, confirmation=False))

    assert result.ok is False
    assert result.status == 'blocked_by_validation'
    assert result.risk_decision is not None
