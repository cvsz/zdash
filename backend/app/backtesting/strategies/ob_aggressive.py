from __future__ import annotations

from app.backtesting.models import Candle, StrategySignal
from app.backtesting.strategy_base import BaseStrategy


class OBAggressiveStrategy(BaseStrategy):
    name = "ob_aggressive"
    default_parameters = {
        "lookback": 12,
        "risk_reward": 2.0,
        "confidence_threshold": 0.55,
        "atr_multiplier": 1.2,
    }

    def validate_parameters(self, parameters: dict) -> dict:
        merged = super().validate_parameters(parameters)
        lookback = int(merged["lookback"])
        risk_reward = float(merged["risk_reward"])
        confidence_threshold = float(merged["confidence_threshold"])
        atr_multiplier = float(merged["atr_multiplier"])
        if lookback < 5:
            raise ValueError("lookback must be >= 5")
        if risk_reward <= 0:
            raise ValueError("risk_reward must be > 0")
        if not 0 <= confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be in [0,1]")
        if atr_multiplier <= 0:
            raise ValueError("atr_multiplier must be > 0")
        merged.update(
            {
                "lookback": lookback,
                "risk_reward": risk_reward,
                "confidence_threshold": confidence_threshold,
                "atr_multiplier": atr_multiplier,
            }
        )
        return merged

    def generate_signal(self, candles: list[Candle], index: int, parameters: dict) -> StrategySignal:
        p = self.validate_parameters(parameters)
        candle = candles[index]
        symbol = "XAUUSD"
        timeframe = "M5"

        if index < p["lookback"]:
            return self.hold_signal(
                candle=candle,
                symbol=symbol,
                timeframe=timeframe,
                metadata={"reason": "insufficient_history"},
            )

        window = candles[index - p["lookback"] : index]
        prior_close = candles[index - 1].close
        window_high = max(item.high for item in window)
        window_low = min(item.low for item in window)
        volatility = self.volatility(window)
        impulse = abs(candle.close - prior_close) / volatility
        breakout_distance = max(
            abs(candle.close - window_high),
            abs(candle.close - window_low),
        )
        confidence = min(1.0, 0.45 + (impulse * 0.2) + (breakout_distance / volatility * 0.15))

        direction = "hold"
        if candle.close > window_high and confidence >= p["confidence_threshold"]:
            direction = "buy"
        elif candle.close < window_low and confidence >= p["confidence_threshold"]:
            direction = "sell"

        stop_distance = volatility * p["atr_multiplier"]
        if direction == "buy":
            stop_loss = candle.close - stop_distance
            take_profit = candle.close + (stop_distance * p["risk_reward"])
        elif direction == "sell":
            stop_loss = candle.close + stop_distance
            take_profit = candle.close - (stop_distance * p["risk_reward"])
        else:
            return self.hold_signal(
                candle=candle,
                symbol=symbol,
                timeframe=timeframe,
                confidence=confidence,
                metadata={"reason": "no_breakout"},
            )

        return self.build_signal(
            candle=candle,
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            entry=candle.close,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            metadata={"lookback": p["lookback"], "volatility": round(volatility, 6)},
        )
