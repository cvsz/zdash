from datetime import UTC, datetime, timedelta

import pytest

from app.core.outbox_delivery import plan_retry, truncate_error
from app.trading.indicators import (
    adx,
    atr,
    bollinger_bands,
    ema,
    ichimoku,
    macd,
    max_drawdown_pct,
    rate_of_change,
    realized_volatility_pct,
    rsi,
    sma,
    vwap,
)
from app.trading.instrument_registry import (
    DEFAULT_INSTRUMENTS,
    InstrumentMetadata,
    InstrumentRegistry,
    validate_order_price,
)
from app.trading.market_session import MarketSessionPolicy
from app.trading.models import Candle


def _candles(closes: list[float], volume: float = 100.0) -> list[Candle]:
    base = datetime(2026, 8, 23, tzinfo=UTC)
    return [
        Candle(
            timestamp=base + timedelta(minutes=i),
            open=close,
            high=close + 1.0,
            low=close - 1.0,
            close=close,
            volume=volume,
        )
        for i, close in enumerate(closes)
    ]


# --- indicators ---------------------------------------------------------------


def test_sma_and_ema() -> None:
    assert sma([1.0, 2.0, 3.0, 4.0], period=2) == 3.5
    assert sma([1.0], period=2) is None
    assert ema(list(range(1, 21)), period=10) is not None
    assert ema([1.0, 2.0], period=10) is None


def test_macd_returns_line_signal_histogram() -> None:
    values = [float(i % 7) + 1.0 for i in range(50)]
    result = macd(values)
    assert result is not None
    line, signal, histogram = result
    assert histogram == pytest.approx(line - signal)


def test_rsi_bounds_and_extremes() -> None:
    rising = [float(i) for i in range(30)]
    assert rsi(rising) == 100.0
    falling = [30.0 - float(i) for i in range(30)]
    value = rsi(falling)
    assert value is not None and value < 5


def test_atr_vwap_bollinger() -> None:
    candles = _candles([2300.0 + i * 0.5 for i in range(20)])
    atr_value = atr(candles, period=14)
    assert atr_value is not None and atr_value > 0

    vwap_value = vwap(candles, period=10)
    # Typical price of each candle equals its close (high/low are +/-1).
    expected_vwap = sum(2300.0 + i * 0.5 for i in range(10, 20)) / 10
    assert vwap_value == pytest.approx(expected_vwap)

    bands = bollinger_bands([1.0] * 20)
    assert bands is not None
    lower, middle, upper = bands
    assert lower == middle == upper == 1.0

    trending = bollinger_bands([float(i) for i in range(1, 31)])
    assert trending is not None
    assert trending[1] == pytest.approx(20.5)  # mean of the trailing 20-value window


def test_adx_ichimoku_roc_realized_vol() -> None:
    candles = _candles([2300.0 + (i % 5) * 2.0 for i in range(40)])
    adx_value = adx(candles, period=14)
    if adx_value is not None:
        assert 0 <= adx_value <= 100

    long_candles = _candles([2300.0 + i * 0.25 for i in range(60)])
    ich = ichimoku(long_candles)
    assert ich is not None and len(ich) == 4

    roc = rate_of_change([100.0, 110.0], period=1)
    assert roc == pytest.approx(10.0)

    vol = realized_volatility_pct([100.0 * (1 + 0.001 * i) for i in range(25)])
    assert vol is not None and vol >= 0


def test_max_drawdown_pct() -> None:
    assert max_drawdown_pct([]) == 0.0
    assert max_drawdown_pct([100.0]) == 0.0
    assert max_drawdown_pct([100.0, 120.0, 90.0]) == pytest.approx(25.0)


# --- instrument registry ------------------------------------------------------


def test_registry_validates_tick_and_band() -> None:
    registry = InstrumentRegistry()
    registry.upsert(
        InstrumentMetadata(
            symbol="xauusd",
            tick_size=0.01,
            lower_price_band=2000.0,
            upper_price_band=3000.0,
        )
    )
    known, band_ok, tick_ok = registry.validate_price("XAUUSD", 2300.55)
    assert known and band_ok and tick_ok

    _, band_bad, _ = registry.validate_price("XAUUSD", 3500.0)
    assert band_bad is False

    _, _, tick_bad = registry.validate_price("XAUUSD", 2300.555)
    assert tick_bad is False


def test_validate_order_price_verdicts() -> None:
    registry = InstrumentRegistry()
    registry.upsert(InstrumentMetadata(symbol="XAUUSD", tick_size=0.01))
    assert validate_order_price(registry, "XAUUSD", 2300.0) == "accepted"
    assert validate_order_price(registry, "AAPL", 100.0) == "unknown_instrument"
    assert validate_order_price(registry, "XAUUSD", None) == "accepted"


def test_default_instruments_cover_xauusd() -> None:
    registry = InstrumentRegistry()
    for metadata in DEFAULT_INSTRUMENTS:
        registry.upsert(metadata)
    assert validate_order_price(registry, "XAUUSD", 2300.01) == "accepted"
    assert validate_order_price(registry, "XAUUSD", 2300.011) == "tick_violation"


def test_registry_load_json_and_normalizes_symbol() -> None:
    registry = InstrumentRegistry('[{"symbol": " xauusd ", "tick_size": 0.01}]')
    assert registry.get("XAUUSD") is not None
    with pytest.raises(ValueError):
        registry.load_json("not-a-list")


# --- market session policy ----------------------------------------------------


def test_session_open_during_configured_window() -> None:
    policy = MarketSessionPolicy(
        timezone_name="Asia/Bangkok",
        sessions="09:00-12:00,13:00-16:30",
        holidays="2026-08-14",
    )
    # 2026-08-12 is a Wednesday.
    noon = datetime(2026, 8, 12, 10, 0, tzinfo=UTC)  # 17:00 Bangkok -> closed
    known, opened = policy.state(noon)
    assert known is True and opened is False

    morning = datetime(2026, 8, 12, 3, 0, tzinfo=UTC)  # 10:00 Bangkok -> open
    known, opened = policy.state(morning)
    assert known is True and opened is True


def test_holiday_and_weekend_fail_closed() -> None:
    policy = MarketSessionPolicy(
        timezone_name="Asia/Bangkok",
        sessions="09:00-16:30",
        holidays="2026-08-14",
    )
    known, opened = policy.state(datetime(2026, 8, 14, 2, 0, tzinfo=UTC))
    assert (known, opened) == (True, False)

    # 2026-08-15 is a Saturday.
    known, opened = policy.state(datetime(2026, 8, 15, 2, 0, tzinfo=UTC))
    assert (known, opened) == (True, False)


def test_explain_reports_reason_and_sessions() -> None:
    policy = MarketSessionPolicy(
        timezone_name="Asia/Bangkok",
        sessions="09:00-16:30",
        holidays="2026-08-14",
    )
    report = policy.explain(datetime(2026, 8, 14, 2, 0, tzinfo=UTC))
    assert report["known"] is True
    assert report["source"] == "holiday"
    assert report["open"] is False


def test_unknown_timezone_rejected() -> None:
    with pytest.raises(ValueError):
        MarketSessionPolicy(timezone_name="Mars/Olympus", sessions="09:00-17:00")


# --- outbox delivery ----------------------------------------------------------


def test_retry_plan_backoff_and_dead_letter() -> None:
    now = datetime(2026, 8, 23, 12, 0, tzinfo=UTC)
    plan = plan_retry(
        attempt_count=1,
        base_seconds=10,
        max_seconds=600,
        max_attempts=5,
        now=now,
    )
    assert plan.next_attempt_at == now + timedelta(seconds=10)
    assert plan.dead_lettered is False

    plan = plan_retry(
        attempt_count=3,
        base_seconds=10,
        max_seconds=600,
        max_attempts=5,
        now=now,
    )
    assert plan.next_attempt_at == now + timedelta(seconds=40)

    plan = plan_retry(
        attempt_count=5,
        base_seconds=10,
        max_seconds=600,
        max_attempts=5,
        now=now,
    )
    assert plan.dead_lettered is True
    assert plan.dead_lettered_at == now


def test_truncate_error_caps_length() -> None:
    assert truncate_error("short") == "short"
    assert len(truncate_error("x" * 999)) == 500
    assert truncate_error("x" * 999).endswith("...")
    with pytest.raises(ValueError):
        truncate_error("x", limit=-1)
