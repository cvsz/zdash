from app.risk.halt_flag import HaltFlagStore
from app.risk.kill_switch import KillSwitch
from app.risk.models import DrawdownResult


def _drawdown(total: float, daily: float, risk_level: str = "danger") -> DrawdownResult:
    return DrawdownResult(
        current_equity=10000.0 - total,
        peak_equity=10000.0,
        daily_start_equity=10000.0,
        total_drawdown_percent=total,
        daily_drawdown_percent=daily,
        floating_pnl=-total,
        risk_level=risk_level,
        breached=total >= 20,
        breach_reason=None,
    )


def test_does_not_trigger_below_threshold() -> None:
    switch = KillSwitch()
    assert switch.should_trigger(_drawdown(total=10.0, daily=2.0)) is False


def test_triggers_at_emergency_threshold() -> None:
    switch = KillSwitch()
    assert (
        switch.should_trigger(_drawdown(total=50.0, daily=5.0, risk_level="emergency"))
        is True
    )


def test_activates_halt_state_and_reason_includes_drawdown() -> None:
    switch = KillSwitch()
    store = HaltFlagStore()
    state = switch.trigger(
        _drawdown(total=50.0, daily=5.0, risk_level="emergency"), store
    )
    assert state.halted is True
    assert state.reason is not None
    assert "total_drawdown=50.0%" in state.reason
