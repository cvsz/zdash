from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import get_settings
from app.trading.models import Candle, TradingSignal


class FunnelFilter:
    def __init__(
        self,
        fast: int | None = None,
        medium: int | None = None,
        slow: int | None = None,
    ) -> None:
        settings = get_settings()
        self.fast = fast or settings.funnel_fast_period
        self.medium = medium or settings.funnel_medium_period
        self.slow = slow or settings.funnel_slow_period

    @staticmethod
    def calculate_sma(values: list[float], period: int) -> list[float]:
        if period <= 0:
            raise ValueError("period must be positive")
        if not values:
            return []

        result: list[float] = []
        running_sum = 0.0
        for idx, value in enumerate(values):
            running_sum += value
            if idx >= period:
                running_sum -= values[idx - period]

            window = min(idx + 1, period)
            result.append(running_sum / window)
        return result

    def evaluate(self, candles: list[Candle]) -> dict:
        if len(candles) < self.fast:
            raise ValueError(f"need at least {self.fast} candles for funnel evaluation")

        closes = [candle.close for candle in candles]
        sma_fast_series = self.calculate_sma(closes, self.fast)
        sma_medium_series = self.calculate_sma(closes, self.medium)
        sma_slow_series = self.calculate_sma(closes, self.slow)

        sma_fast = sma_fast_series[-1]
        sma_medium = sma_medium_series[-1]
        sma_slow = sma_slow_series[-1]
        latest_close = closes[-1]

        direction = "hold"
        if latest_close > sma_fast and sma_slow > sma_medium > sma_fast:
            direction = "buy"
        elif latest_close < sma_fast and sma_slow < sma_medium < sma_fast:
            direction = "sell"

        return {
            "direction": direction,
            "close": round(latest_close, 4),
            "sma_fast": round(sma_fast, 4),
            "sma_medium": round(sma_medium, 4),
            "sma_slow": round(sma_slow, 4),
            "periods": {
                "fast": self.fast,
                "medium": self.medium,
                "slow": self.slow,
            },
        }

    def generate_signal(
        self, candles: list[Candle], symbol: str, timeframe: str
    ) -> TradingSignal:
        state = self.evaluate(candles)
        latest = candles[-1]

        recent = candles[-20:]
        avg_range = sum(c.high - c.low for c in recent) / len(recent)
        volatility = max(avg_range, 0.2)

        direction = state["direction"]
        confidence = 0.5
        if direction == "buy":
            confidence = min(
                0.9,
                0.55
                + ((state["sma_slow"] - state["sma_fast"]) / max(volatility, 0.001))
                * 0.03,
            )
            entry = latest.close
            stop_loss = entry - (volatility * 1.5)
            take_profit = entry + (volatility * 3.0)
            reason = "Funnel filter buy bias in simulation mode."
        elif direction == "sell":
            confidence = min(
                0.9,
                0.55
                + ((state["sma_fast"] - state["sma_slow"]) / max(volatility, 0.001))
                * 0.03,
            )
            entry = latest.close
            stop_loss = entry + (volatility * 1.5)
            take_profit = entry - (volatility * 3.0)
            reason = "Funnel filter sell bias in simulation mode."
        else:
            entry = latest.close
            stop_loss = entry
            take_profit = entry
            reason = "Funnel filter hold state in simulation mode."

        return TradingSignal(
            id=str(uuid4()),
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            strategy=get_settings().trading_default_strategy,
            confidence=max(0.0, min(1.0, round(confidence, 4))),
            entry=round(entry, 4),
            stop_loss=round(stop_loss, 4),
            take_profit=round(take_profit, 4),
            reason=reason,
            metadata={
                "funnel_state": state,
                "volatility": round(volatility, 4),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
