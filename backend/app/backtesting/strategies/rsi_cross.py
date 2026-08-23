from __future__ import annotations

from typing import Literal

from app.backtesting.models import Candle, StrategySignal
from app.backtesting.strategy_base import BaseStrategy
from app.trading.indicators import atr as atr_value
from app.trading.indicators import rsi


class RSICrossStrategy(BaseStrategy):
    """RSI oversold/overbought cross strategy (ported from ztrader RSI_CROSS).

    Stateless adaptation: signals fire on the bar where RSI crosses the
    threshold, rather than relying on mutable last-signal state.
    """

    name = "rsi_cross"
    default_parameters = {
        "period": 14,
        "overbought": 70.0,
        "oversold": 30.0,
        "risk_reward": 1.5,
        "atr_multiplier": 1.5,
        "confidence_threshold": 0.0,
    }

    def validate_parameters(self, parameters: dict) -> dict:
        p = super().validate_parameters(parameters)
        period = int(p["period"])
        overbought = float(p["overbought"])
        oversold = float(p["oversold"])
        risk_reward = float(p["risk_reward"])
        atr_multiplier = float(p["atr_multiplier"])
        confidence_threshold = float(p["confidence_threshold"])

        if period < 2:
            raise ValueError("period must be >= 2")
        if not 50.0 < overbought <= 100.0:
            raise ValueError("overbought must be in (50, 100]")
        if not 0.0 <= oversold < 50.0:
            raise ValueError("oversold must be in [0, 50)")
        if risk_reward <= 0:
            raise ValueError("risk_reward must be > 0")
        if atr_multiplier <= 0:
            raise ValueError("atr_multiplier must be > 0")
        if not 0 <= confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be in [0,1]")

        p.update(
            {
                "period": period,
                "overbought": overbought,
                "oversold": oversold,
                "risk_reward": risk_reward,
                "atr_multiplier": atr_multiplier,
                "confidence_threshold": confidence_threshold,
            }
        )
        return p

    def generate_signal(
        self, candles: list[Candle], index: int, parameters: dict
    ) -> StrategySignal:
        p = self.validate_parameters(parameters)
        candle = candles[index]
        period = int(p["period"])

        closes = [item.close for item in candles[: index + 1]]
        values = rsi(closes, period=period)
        if values is None or len(closes) < period + 2:
            return self.hold_signal(
                candle=candle,
                symbol="XAUUSD",
                timeframe="M5",
                metadata={"reason": "insufficient_history"},
            )

        previous_values = rsi(closes[:-1], period=period)
        if previous_values is None:
            return self.hold_signal(
                candle=candle,
                symbol="XAUUSD",
                timeframe="M5",
                metadata={"reason": "insufficient_history"},
            )

        oversold = float(p["oversold"])
        overbought = float(p["overbought"])

        crossed_into_oversold = previous_values >= oversold > values
        crossed_into_overbought = previous_values <= overbought < values

        direction: Literal["buy", "sell", "hold"] = "hold"
        if crossed_into_oversold:
            direction = "buy"
        elif crossed_into_overbought:
            direction = "sell"

        confidence = min(1.0, abs(values - 50.0) / 50.0)
        if direction == "hold" or confidence < float(p["confidence_threshold"]):
            return self.hold_signal(
                candle=candle,
                symbol="XAUUSD",
                timeframe="M5",
                confidence=confidence,
                metadata={"reason": "no_cross", "rsi": round(values, 2)},
            )

        atr_stop = atr_value(candles[: index + 1], period=min(period, index)) or (
            candle.close * 0.002
        )
        stop_distance = max(atr_stop * float(p["atr_multiplier"]), candle.close * 0.001)

        if direction == "buy":
            stop_loss = candle.close - stop_distance
            take_profit = candle.close + stop_distance * float(p["risk_reward"])
        else:
            stop_loss = candle.close + stop_distance
            take_profit = candle.close - stop_distance * float(p["risk_reward"])

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
                "rsi": round(values, 2),
                "previous_rsi": round(previous_values, 2),
            },
        )
