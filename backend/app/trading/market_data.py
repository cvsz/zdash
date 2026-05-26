from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import sin

from app.trading.models import Candle


def generate_mock_xauusd_m5_candles(limit: int = 300) -> list[Candle]:
    safe_limit = max(limit, 300)
    now = datetime.now(timezone.utc)
    base_price = 2325.0
    candles: list[Candle] = []

    for index in range(safe_limit):
        trend_component = index * 0.09
        cycle_component = sin(index / 8.0) * 1.4
        pullback_component = -0.8 if index % 37 in {8, 9, 10} else 0.0

        open_price = base_price + trend_component + cycle_component + pullback_component
        close_delta = 0.28 if index % 2 == 0 else -0.19
        close_price = open_price + close_delta

        wick = 0.34 + abs(sin(index / 5.0)) * 0.22
        high_price = max(open_price, close_price) + wick
        low_price = min(open_price, close_price) - wick

        candles.append(
            Candle(
                timestamp=now - timedelta(minutes=(safe_limit - index) * 5),
                open=round(open_price, 4),
                high=round(high_price, 4),
                low=round(low_price, 4),
                close=round(close_price, 4),
                volume=1000 + index,
            )
        )

    return candles
