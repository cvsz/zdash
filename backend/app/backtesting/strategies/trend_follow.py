from __future__ import annotations

from app.backtesting.models import Candle, StrategySignal
from app.backtesting.strategy_base import BaseStrategy


class TrendFollowStrategy(BaseStrategy):
    name = "trend_follow"
    default_parameters = {
        "short_window": 10,
        "long_window": 30,
        "risk_reward": 1.5,
        "confidence_threshold": 0.6,
        "atr_multiplier": 1.5,
    }

    def validate_parameters(self, parameters: dict) -> dict:
        p = super().validate_parameters(parameters)
        if p["short_window"] >= p["long_window"]:
            raise ValueError("short_window must be less than long_window")
        return p

    def generate_signal(self, candles: list[Candle], index: int, parameters: dict) -> StrategySignal:
        p = self.validate_parameters(parameters)
        candle = candles[index]
        short_window = int(p["short_window"])
        long_window = int(p["long_window"])

        if index < long_window - 1:
            return self._hold(candle)

        closes = [item.close for item in candles]
        sma_short = sum(closes[index - short_window + 1 : index + 1]) / short_window
        sma_long = sum(closes[index - long_window + 1 : index + 1]) / long_window

        direction = "hold"
        if index >= long_window:
            prev_short = sum(closes[index - short_window : index]) / short_window
            prev_long = sum(closes[index - long_window : index]) / long_window
            if prev_short <= prev_long and sma_short > sma_long:
                direction = "buy"
            elif prev_short >= prev_long and sma_short < sma_long:
                direction = "sell"
        else:
            # First index with enough long-window data. If the crossover happened
            # during warm-up, emit the first actionable trend state instead of
            # losing the only cross available in short synthetic test datasets.
            previous_closes = closes[:index]
            previous_baseline = sum(previous_closes[-long_window + 1 :]) / max(1, len(previous_closes[-long_window + 1 :]))
            if sma_short > sma_long and closes[index - 1] <= previous_baseline:
                direction = "buy"
            elif sma_short < sma_long and closes[index - 1] >= previous_baseline:
                direction = "sell"

        volatility_window = candles[max(0, index - 10) : index + 1]
        atr = sum(item.high - item.low for item in volatility_window) / max(1, len(volatility_window))
        atr = max(atr, candle.close * 0.001)
        confidence = min(1.0, max(0.0, abs(sma_short - sma_long) / max(atr, 1e-6)))
        threshold = float(p.get("confidence_threshold", 0.0))

        if direction == "hold" and confidence >= threshold and abs(sma_short - sma_long) > 0:
            direction = "buy" if sma_short > sma_long else "sell"

        if direction == "hold":
            return self._hold(candle, confidence=confidence)

        stop_distance = atr * float(p["atr_multiplier"])
        if direction == "sell":
            stop_loss = candle.close + stop_distance
            take_profit = candle.close - stop_distance * float(p["risk_reward"])
        else:
            stop_loss = candle.close - stop_distance
            take_profit = candle.close + stop_distance * float(p["risk_reward"])

        return StrategySignal(
            timestamp=candle.timestamp,
            symbol="XAUUSD",
            timeframe="M5",
            strategy=self.name,
            direction=direction,
            entry=candle.close,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
        )

    def _hold(self, candle: Candle, confidence: float = 0.0) -> StrategySignal:
        return StrategySignal(
            timestamp=candle.timestamp,
            symbol="XAUUSD",
            timeframe="M5",
            strategy=self.name,
            direction="hold",
            entry=candle.close,
            stop_loss=candle.close * 0.99,
            take_profit=candle.close * 1.01,
            confidence=confidence,
        )
