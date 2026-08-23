from __future__ import annotations

from typing import Literal

from app.backtesting.models import Candle, StrategySignal
from app.backtesting.strategy_base import BaseStrategy
from app.trading.indicators import vwap as vwap_value


class VWAPStrategy(BaseStrategy):
    """VWAP deviation reversion (ported from ztrader VWAP).

    Uses the trailing window VWAP (rather than cumulative session VWAP) so the
    strategy stays deterministic and stateless per bar.
    """

    name = "vwap"
    default_parameters = {
        "window": 30,
        "threshold": 0.02,
        "risk_reward": 1.5,
        "stop_fraction": 0.005,
        "confidence_threshold": 0.0,
    }

    def validate_parameters(self, parameters: dict) -> dict:
        p = super().validate_parameters(parameters)
        window = int(p["window"])
        threshold = float(p["threshold"])
        risk_reward = float(p["risk_reward"])
        stop_fraction = float(p["stop_fraction"])
        confidence_threshold = float(p["confidence_threshold"])

        if window < 5:
            raise ValueError("window must be >= 5")
        if not 0 < threshold < 1:
            raise ValueError("threshold must be in (0, 1)")
        if risk_reward <= 0:
            raise ValueError("risk_reward must be > 0")
        if not 0 < stop_fraction < 0.1:
            raise ValueError("stop_fraction must be in (0, 0.1)")
        if not 0 <= confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be in [0,1]")

        p.update(
            {
                "window": window,
                "threshold": threshold,
                "risk_reward": risk_reward,
                "stop_fraction": stop_fraction,
                "confidence_threshold": confidence_threshold,
            }
        )
        return p

    def generate_signal(
        self, candles: list[Candle], index: int, parameters: dict
    ) -> StrategySignal:
        p = self.validate_parameters(parameters)
        candle = candles[index]
        window = int(p["window"])

        history = candles[: index + 1]
        if len(history) < max(window + 1, 6):
            return self.hold_signal(
                candle=candle,
                symbol="XAUUSD",
                timeframe="M5",
                metadata={"reason": "insufficient_history"},
            )

        current_vwap = vwap_value(history[-window:])
        previous_vwap = vwap_value(history[-window - 1 : -1])
        if current_vwap is None or previous_vwap is None or current_vwap <= 0:
            return self.hold_signal(
                candle=candle,
                symbol="XAUUSD",
                timeframe="M5",
                metadata={"reason": "no_volume_data"},
            )

        deviation = (candle.close - current_vwap) / current_vwap
        previous_deviation = (candles[index - 1].close - previous_vwap) / previous_vwap

        threshold = float(p["threshold"])
        direction: Literal["buy", "sell", "hold"] = "hold"
        # Cross below -threshold -> buy; cross above +threshold -> sell.
        if previous_deviation >= -threshold > deviation:
            direction = "buy"
        elif previous_deviation <= threshold < deviation:
            direction = "sell"

        confidence = min(1.0, abs(deviation) / (threshold * 2))
        if direction == "hold" or confidence < float(p["confidence_threshold"]):
            return self.hold_signal(
                candle=candle,
                symbol="XAUUSD",
                timeframe="M5",
                confidence=confidence,
                metadata={"reason": "no_cross", "deviation": round(deviation, 5)},
            )

        stop_distance = max(candle.close * float(p["stop_fraction"]), 1e-6)
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
                "vwap": round(current_vwap, 6),
                "deviation": round(deviation, 5),
            },
        )
