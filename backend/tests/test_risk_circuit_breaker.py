from datetime import UTC, datetime, timedelta

import pytest

from app.risk.circuit_breaker import CircuitBreaker
from app.risk.halt_flag import HaltFlagStore

_BASE = datetime(2026, 8, 23, 12, 0, tzinfo=UTC)


def _ts(minute: int) -> datetime:
    return _BASE + timedelta(minutes=minute)


def test_allows_trades_when_healthy() -> None:
    breaker = CircuitBreaker()
    decision = breaker.evaluate(now=_ts(0))
    assert decision.allowed is True
    assert decision.reason == "ok"


def test_trips_after_consecutive_losses() -> None:
    breaker = CircuitBreaker(max_consecutive_losses=3)
    assert breaker.record_trade_outcome(-10.0, now=_ts(1)) is False
    assert breaker.record_trade_outcome(-5.0, now=_ts(2)) is False
    tripped = breaker.record_trade_outcome(-1.0, now=_ts(3))
    assert tripped is True

    decision = breaker.evaluate(now=_ts(4))
    assert decision.allowed is False
    assert decision.reason == "circuit_tripped"


def test_win_resets_loss_streak() -> None:
    breaker = CircuitBreaker(max_consecutive_losses=3)
    breaker.record_trade_outcome(-10.0, now=_ts(1))
    breaker.record_trade_outcome(-5.0, now=_ts(2))
    breaker.record_trade_outcome(+2.0, now=_ts(3))
    assert breaker.consecutive_losses == 0

    tripped = breaker.record_trade_outcome(-1.0, now=_ts(4))
    assert tripped is False
    assert breaker.consecutive_losses == 1


def test_cooldown_expires_and_resets() -> None:
    breaker = CircuitBreaker(max_consecutive_losses=1, cooldown_minutes=60)
    breaker.record_trade_outcome(-10.0, now=_ts(0))

    assert breaker.is_tripped(now=_ts(30)) is True
    assert breaker.is_tripped(now=_ts(61)) is False
    assert breaker.consecutive_losses == 0

    decision = breaker.evaluate(now=_ts(62))
    assert decision.allowed is True


def test_rate_limit_blocks_when_hourly_allowance_exhausted() -> None:
    breaker = CircuitBreaker(max_trades_per_hour=3)
    for minute in (1, 2, 3):
        breaker.record_trade_outcome(+1.0, now=_ts(minute))

    decision = breaker.evaluate(now=_ts(4))
    assert decision.allowed is False
    assert decision.reason == "rate_limit_exceeded"


def test_rate_limit_window_slides() -> None:
    breaker = CircuitBreaker(max_trades_per_hour=2)
    breaker.record_trade_outcome(+1.0, now=_ts(0))
    breaker.record_trade_outcome(+1.0, now=_ts(5))

    # First trade falls out of the 1h window at _ts(61).
    assert breaker.check_trade_rate_limit(now=_ts(66)) is False


def test_zero_pnl_counts_as_loss() -> None:
    breaker = CircuitBreaker(max_consecutive_losses=1)
    tripped = breaker.record_trade_outcome(0.0, now=_ts(0))
    assert tripped is True
    assert breaker.consecutive_losses == 1


def test_trip_publishes_halt_flag() -> None:
    halt_store = HaltFlagStore()
    breaker = CircuitBreaker(halt_store=halt_store, max_consecutive_losses=1)
    breaker.record_trade_outcome(-25.0, now=_ts(0))

    state = halt_store.get_state()
    assert state.halted is True
    assert state.source == "circuit_breaker"
    assert "consecutive losses" in (state.reason or "")


def test_status_reflects_state() -> None:
    breaker = CircuitBreaker(max_consecutive_losses=2, max_trades_per_hour=10)
    breaker.record_trade_outcome(-1.0, now=_ts(1))
    status = breaker.get_status(now=_ts(2))

    assert status.is_tripped is False
    assert status.consecutive_losses == 1
    assert status.trades_last_hour == 1
    assert status.tripped_until is None


def test_invalid_configuration_rejected() -> None:
    with pytest.raises(ValueError):
        CircuitBreaker(max_consecutive_losses=0)
    with pytest.raises(ValueError):
        CircuitBreaker(cooldown_minutes=0)
    with pytest.raises(ValueError):
        CircuitBreaker(max_trades_per_hour=0)


def test_old_trades_pruned_from_history() -> None:
    breaker = CircuitBreaker()
    breaker.record_trade_outcome(+1.0, now=_ts(0))
    breaker.get_status(now=_ts(90))
    assert breaker.recent_trades == []
