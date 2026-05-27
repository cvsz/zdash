from __future__ import annotations

from typing import Literal

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
        short_window = int(p["short_window"])
        long_window = int(p["long_window"])
        risk_reward = float(p["risk_reward"])
        confidence_threshold = float(p["confidence_threshold"])
        atr_multiplier = float(p["atr_multiplier"])
        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window")
        if short_window < 2 or long_window < 5:
            raise ValueError("moving-average windows are too small")
        if risk_reward <= 0:
            raise ValueError("risk_reward must be > 0")
        if not 0 <= confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be in [0,1]")
        if atr_multiplier <= 0:
            raise ValueError("atr_multiplier must be > 0")
        p.update(
            {
                "short_window": short_window,
                "long_window": long_window,
                "risk_reward": risk_reward,
                "confidence_threshold": confidence_threshold,
                "atr_multiplier": atr_multiplier,
            }
        )
        return p

    def generate_signal(
        self, candles: list[Candle], index: int, parameters: dict
    ) -> StrategySignal:
        p = self.validate_parameters(parameters)
        candle = candles[index]
        short_window = int(p["short_window"])
        long_window = int(p["long_window"])

        if index < long_window - 1:
            return self.hold_signal(
                candle=candle,
                symbol="XAUUSD",
                timeframe="M5",
                metadata={"reason": "insufficient_history"},
            )

        closes = [item.close for item in candles]
        sma_short = sum(closes[index - short_window + 1 : index + 1]) / short_window
        sma_long = sum(closes[index - long_window + 1 : index + 1]) / long_window

        direction: Literal["buy", "sell", "hold"] = "hold"
        if index >= long_window:
            prev_short = sum(closes[index - short_window : index]) / short_window
            prev_long = sum(closes[index - long_window : index]) / long_window
            if prev_short <= prev_long and sma_short > sma_long:
                direction = "buy"
            elif prev_short >= prev_long and sma_short < sma_long:
                direction = "sell"
        else:
            # First long-window index fallback for small synthetic datasets.
            previous_closes = closes[:index]
            baseline_window = previous_closes[-long_window + 1 :]
            previous_baseline = sum(baseline_window) / max(1, len(baseline_window))
            if sma_short > sma_long and closes[index - 1] <= previous_baseline:
                direction = "buy"
            elif sma_short < sma_long and closes[index - 1] >= previous_baseline:
                direction = "sell"

        volatility_window = candles[max(0, index - 10) : index + 1]
        atr = sum(item.high - item.low for item in volatility_window) / max(
            1, len(volatility_window)
        )
        atr = max(atr, candle.close * 0.001)
        confidence = min(1.0, max(0.0, abs(sma_short - sma_long) / max(atr, 1e-6)))
        threshold = float(p.get("confidence_threshold", 0.0))

        if (
            direction == "hold"
            and confidence >= threshold
            and abs(sma_short - sma_long) > 0
        ):
            direction = "buy" if sma_short > sma_long else "sell"

        if direction == "hold":
            return self.hold_signal(
                candle=candle,
                symbol="XAUUSD",
                timeframe="M5",
                confidence=confidence,
                metadata={
                    "reason": "no_cross_or_low_confidence",
                    "ma_gap": round(abs(sma_short - sma_long), 6),
                },
            )

        stop_distance = atr * float(p["atr_multiplier"])
        if direction == "sell":
            stop_loss = candle.close + stop_distance
            take_profit = candle.close - stop_distance * float(p["risk_reward"])
        else:
            stop_loss = candle.close - stop_distance
            take_profit = candle.close + stop_distance * float(p["risk_reward"])

        return self.build_signal(
            candle=candle,
            symbol="XAUUSD",
            timeframe="M5",
            direction=direction,
            entry=candle.close,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            metadata={
                "short_sma": round(sma_short, 6),
                "long_sma": round(sma_long, 6),
                "ma_gap": round(abs(sma_short - sma_long), 6),
            },
        )
