from datetime import datetime, timedelta, timezone

from app.trading.execution_engine import ExecutionEngine
from app.trading.models import TradingSignal
from app.trading.signal_validation import SignalValidationService


def _base_signal() -> TradingSignal:
    return TradingSignal(
        symbol='XAUUSD',
        timeframe='M5',
        direction='buy',
        strategy='ob_aggressive',
        confidence=0.72,
        entry=2300.0,
        stop_loss=2298.0,
        take_profit=2304.0,
        reason='validation test',
    )


def test_valid_buy_passes() -> None:
    service = SignalValidationService()
    result = service.validate(_base_signal())

    assert result.valid is True


def test_invalid_sl_tp_fails() -> None:
    service = SignalValidationService()
    signal = _base_signal().model_copy(update={'stop_loss': 2301.0, 'take_profit': 2299.0})
    result = service.validate(signal)

    assert result.valid is False


def test_old_signal_fails() -> None:
    service = SignalValidationService()
    old_time = datetime.now(timezone.utc) - timedelta(hours=2)
    signal = _base_signal().model_copy(update={'created_at': old_time})
    result = service.validate(signal)

    assert result.valid is False


def test_hold_signal_does_not_execute() -> None:
    engine = ExecutionEngine()
    hold_signal = _base_signal().model_copy(
        update={
            'direction': 'hold',
            'stop_loss': 2300.0,
            'take_profit': 2300.0,
        }
    )
    result = engine.execute({'signal': hold_signal, 'dry_run': True, 'confirmation': False})

    assert result.status == 'blocked_by_validation'
