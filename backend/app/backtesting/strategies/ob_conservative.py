from __future__ import annotations

from typing import Literal

from app.backtesting.models import Candle, StrategySignal
from app.backtesting.strategy_base import BaseStrategy


class OBConservativeStrategy(BaseStrategy):
    name = "ob_conservative"
    default_parameters = {
        "lookback": 24,
        "risk_reward": 1.8,
        "confidence_threshold": 0.68,
        "atr_multiplier": 1.8,
    }

    def validate_parameters(self, parameters: dict) -> dict:
        merged = super().validate_parameters(parameters)
        lookback = int(merged["lookback"])
        risk_reward = float(merged["risk_reward"])
        confidence_threshold = float(merged["confidence_threshold"])
        atr_multiplier = float(merged["atr_multiplier"])
        if lookback < 8:
            raise ValueError("lookback must be >= 8")
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

    def generate_signal(
        self, candles: list[Candle], index: int, parameters: dict
    ) -> StrategySignal:
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
        window_high = max(item.high for item in window)
        window_low = min(item.low for item in window)
        start_close = window[0].close
        end_close = window[-1].close
        trend_strength = abs(end_close - start_close) / max(
            self.volatility(window), 1e-6
        )
        breakout_strength = abs(candle.close - end_close) / max(
            self.volatility(window) * 1.8, 1e-6
        )
        conf = min(1.0, 0.45 + (trend_strength * 0.15) + breakout_strength)
        direction: Literal["buy", "sell", "hold"] = "hold"

        if (
            candle.close > window_high * 1.0005
            and end_close > start_close
            and conf >= p["confidence_threshold"]
        ):
            direction = "buy"
        elif (
            candle.close < window_low * 0.9995
            and end_close < start_close
            and conf >= p["confidence_threshold"]
        ):
            direction = "sell"

        stop_distance = self.volatility(window) * p["atr_multiplier"]
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
                confidence=conf,
                metadata={"reason": "no_confirmed_breakout"},
            )

        return self.build_signal(
            candle=candle,
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            entry=candle.close,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=conf,
            metadata={
                "lookback": p["lookback"],
                "trend_strength": round(trend_strength, 6),
            },
        )
