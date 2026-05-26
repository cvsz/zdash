from datetime import datetime, timedelta, timezone

from app.backtesting.metrics import BacktestMetricsCalculator
from app.backtesting.models import SimulatedTrade


def _trade(
    *,
    pnl: float,
    entry_time: datetime,
    exit_time: datetime,
    rr: float = 1.0,
) -> SimulatedTrade:
    return SimulatedTrade(
        id=f"trade-{entry_time.timestamp()}",
        symbol="XAUUSD",
        timeframe="M5",
        strategy="ob_aggressive",
        direction="buy",
        entry_time=entry_time,
        exit_time=exit_time,
        entry_price=2300.0,
        exit_price=2301.0,
        stop_loss=2299.0,
        take_profit=2302.0,
        size=1.0,
        pnl=pnl,
        pnl_percent=(pnl / 10000) * 100,
        rr=rr,
        status="closed",
        exit_reason="take_profit" if pnl >= 0 else "stop_loss",
    )


def test_zero_trades_safe() -> None:
    metrics = BacktestMetricsCalculator().calculate([], 10000, 10000, [(datetime.now(timezone.utc), 10000)])
    assert metrics.total_trades == 0
    assert metrics.win_rate == 0
    assert metrics.profit_factor == 0


def test_win_rate_and_profit_factor_calculation() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    trades = [
        _trade(pnl=100.0, entry_time=start, exit_time=start + timedelta(minutes=5), rr=2.0),
        _trade(pnl=-50.0, entry_time=start + timedelta(minutes=10), exit_time=start + timedelta(minutes=15), rr=-1.0),
    ]
    metrics = BacktestMetricsCalculator().calculate(
        trades,
        10000,
        10050,
        [
            (start, 10000),
            (start + timedelta(minutes=5), 10100),
            (start + timedelta(minutes=15), 10050),
        ],
    )
    assert metrics.win_rate == 50.0
    assert metrics.profit_factor == 2.0


def test_drawdown_and_consecutive_losses_calculation() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    trades = [
        _trade(pnl=100, entry_time=start, exit_time=start + timedelta(minutes=5)),
        _trade(pnl=-40, entry_time=start + timedelta(minutes=10), exit_time=start + timedelta(minutes=15)),
        _trade(pnl=-30, entry_time=start + timedelta(minutes=20), exit_time=start + timedelta(minutes=25)),
        _trade(pnl=20, entry_time=start + timedelta(minutes=30), exit_time=start + timedelta(minutes=35)),
    ]
    metrics = BacktestMetricsCalculator().calculate(
        trades,
        10000,
        10050,
        [
            (start, 10000),
            (start + timedelta(minutes=5), 10100),
            (start + timedelta(minutes=15), 10060),
            (start + timedelta(minutes=25), 10030),
            (start + timedelta(minutes=35), 10050),
        ],
    )
    assert metrics.max_drawdown_percent > 0
    assert metrics.consecutive_losses == 2


def test_monthly_return_table() -> None:
    start = datetime(2026, 1, 31, 23, 50, tzinfo=timezone.utc)
    trades = [
        _trade(pnl=120, entry_time=start, exit_time=start + timedelta(minutes=5)),
        _trade(
            pnl=-20,
            entry_time=start + timedelta(days=1),
            exit_time=start + timedelta(days=1, minutes=5),
        ),
    ]
    metrics = BacktestMetricsCalculator().calculate(
        trades,
        10000,
        10100,
        [
            (start, 10000),
            (start + timedelta(minutes=5), 10120),
            (start + timedelta(days=1, minutes=5), 10100),
        ],
    )
    assert "2026-01" in metrics.monthly_return_table
    assert "2026-02" in metrics.monthly_return_table
