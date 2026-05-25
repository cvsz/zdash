from app.core.config import get_settings
from app.risk.drawdown_guard import DrawdownGuard
from app.risk.models import AccountSnapshot


def _snapshot(**kwargs) -> AccountSnapshot:
    base = {
        'balance': 10000.0,
        'equity': 10000.0,
        'peak_equity': 10000.0,
        'daily_start_equity': 10000.0,
        'open_positions': 0,
        'floating_pnl': 0.0,
        'realized_pnl_today': 0.0,
    }
    base.update(kwargs)
    return AccountSnapshot(**base)


def test_total_drawdown_calculation() -> None:
    guard = DrawdownGuard()
    dd = guard.calculate_total_drawdown(_snapshot(equity=9000.0))
    assert dd == 10.0


def test_daily_drawdown_calculation() -> None:
    guard = DrawdownGuard()
    dd = guard.calculate_daily_drawdown(_snapshot(equity=9500.0, daily_start_equity=10000.0))
    assert dd == 5.0


def test_zero_peak_equity_safety() -> None:
    guard = DrawdownGuard()
    result = guard.evaluate(_snapshot(peak_equity=0.0, daily_start_equity=0.0))
    assert result.total_drawdown_percent == 0.0
    assert result.daily_drawdown_percent == 0.0
    assert result.risk_level == 'warning'


def test_no_negative_drawdown() -> None:
    guard = DrawdownGuard()
    result = guard.evaluate(_snapshot(equity=12000.0, peak_equity=10000.0, daily_start_equity=10000.0))
    assert result.total_drawdown_percent == 0.0
    assert result.daily_drawdown_percent == 0.0


def test_warning_threshold() -> None:
    guard = DrawdownGuard()
    result = guard.evaluate(_snapshot(equity=9300.0, daily_start_equity=9300.0))
    assert result.risk_level == 'warning'
    assert result.breached is False


def test_danger_threshold() -> None:
    guard = DrawdownGuard()
    result = guard.evaluate(_snapshot(equity=7900.0))
    assert result.risk_level == 'danger'
    assert result.breached is True


def test_emergency_threshold() -> None:
    guard = DrawdownGuard()
    result = guard.evaluate(_snapshot(equity=5000.0))
    assert result.risk_level == 'emergency'
    assert result.breached is True
