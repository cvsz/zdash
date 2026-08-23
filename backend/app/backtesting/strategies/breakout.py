from __future__ import annotations

from typing import Literal

from app.backtesting.models import Candle, StrategySignal
from app.backtesting.strategy_base import BaseStrategy


class BreakoutStrategy(BaseStrategy):
    """Donchian-style breakout with volume confirmation (ported from ztrader BREAKOUT)."""

    name = "breakout"
    default_parameters = {
        "lookback": 20,
        "volume_factor": 1.5,
        "risk_reward": 1.5,
        "stop_fraction": 0.005,
    }

    def validate_parameters(self, parameters: dict) -> dict:
        p = super().validate_parameters(parameters)
        lookback = int(p["lookback"])
        volume_factor = float(p["volume_factor"])
        risk_reward = float(p["risk_reward"])
        stop_fraction = float(p["stop_fraction"])

        if lookback < 5:
            raise ValueError("lookback must be >= 5")
        if volume_factor <= 0:
            raise ValueError("volume_factor must be > 0")
        if risk_reward <= 0:
            raise ValueError("risk_reward must be > 0")
        if not 0 < stop_fraction < 0.1:
            raise ValueError("stop_fraction must be in (0, 0.1)")

        p.update(
            {
                "lookback": lookback,
                "volume_factor": volume_factor,
                "risk_reward": risk_reward,
                "stop_fraction": stop_fraction,
            }
        )
        return p

    def generate_signal(
        self, candles: list[Candle], index: int, parameters: dict
    ) -> StrategySignal:
        p = self.validate_parameters(parameters)
        candle = candles[index]
        lookback = int(p["lookback"])

        if index < lookback + 1:
            return self.hold_signal(
                candle=candle,
                symbol="XAUUSD",
                timeframe="M5",
                metadata={"reason": "insufficient_history"},
            )

        window = candles[index - lookback : index]
        recent_high = max(item.high for item in window)
        recent_low = min(item.low for item in window)

        avg_volume = sum(item.volume for item in window) / len(window)
        volume_confirmed = candle.volume > avg_volume * float(p["volume_factor"])

        direction: Literal["buy", "sell", "hold"] = "hold"
        if candle.close > recent_high and volume_confirmed:
            direction = "buy"
        elif candle.close < recent_low and volume_confirmed:
            direction = "sell"

        if direction == "hold":
            return self.hold_signal(
                candle=candle,
                symbol="XAUUSD",
                timeframe="M5",
                metadata={
                    "reason": "no_breakout_or_low_volume",
                    "recent_high": round(recent_high, 6),
                    "recent_low": round(recent_low, 6),
                },
            )

        stop_distance = max(candle.close * float(p["stop_fraction"]), 1e-6)
        if direction == "buy":
            stop_loss = min(recent_low, candle.close - stop_distance)
            take_profit = candle.close + (candle.close - stop_loss) * float(
                p["risk_reward"]
            )
        else:
            stop_loss = max(recent_high, candle.close + stop_distance)
            take_profit = candle.close - (stop_loss - candle.close) * float(
                p["risk_reward"]
            )

        return self.build_signal(
            candle=candle,
            symbol="XAUUSD",
            timeframe="M5",
            direction=direction,
            entry=candle.close,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=0.6 if volume_confirmed else 0.3,
            metadata={
                "recent_high": round(recent_high, 6),
                "recent_low": round(recent_low, 6),
                "volume_confirmed": volume_confirmed,
            },
        )
