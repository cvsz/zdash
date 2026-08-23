from __future__ import annotations

from statistics import mean, pstdev
from typing import Literal

from app.backtesting.models import Candle, StrategySignal
from app.backtesting.strategy_base import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """Bollinger-band z-score mean reversion (ported from ztrader MEAN_REVERSION).

    Stateless adaptation: entries fire on the bar where the z-score crosses the
    entry threshold.
    """

    name = "mean_reversion"
    default_parameters = {
        "window": 20,
        "std_dev_factor": 2.0,
        "z_entry": 2.0,
        "risk_reward": 1.5,
        "stop_fraction": 0.005,
        "confidence_threshold": 0.0,
    }

    def validate_parameters(self, parameters: dict) -> dict:
        p = super().validate_parameters(parameters)
        window = int(p["window"])
        std_dev_factor = float(p["std_dev_factor"])
        z_entry = float(p["z_entry"])
        risk_reward = float(p["risk_reward"])
        stop_fraction = float(p["stop_fraction"])
        confidence_threshold = float(p["confidence_threshold"])

        if window < 5:
            raise ValueError("window must be >= 5")
        if std_dev_factor <= 0:
            raise ValueError("std_dev_factor must be > 0")
        if z_entry <= 0:
            raise ValueError("z_entry must be > 0")
        if risk_reward <= 0:
            raise ValueError("risk_reward must be > 0")
        if not 0 < stop_fraction < 0.1:
            raise ValueError("stop_fraction must be in (0, 0.1)")
        if not 0 <= confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be in [0,1]")

        p.update(
            {
                "window": window,
                "std_dev_factor": std_dev_factor,
                "z_entry": z_entry,
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

        if index < window + 1:
            return self.hold_signal(
                candle=candle,
                symbol="XAUUSD",
                timeframe="M5",
                metadata={"reason": "insufficient_history"},
            )

        def _z_score(values: list[float]) -> float | None:
            m = mean(values)
            sd = pstdev(values)
            if sd == 0:
                return None
            return (values[-1] - m) / sd

        current_window = [
            item.close for item in candles[index - window + 1 : index + 1]
        ]
        previous_window = [item.close for item in candles[index - window : index]]

        z_current = _z_score(current_window)
        z_previous = _z_score(previous_window)
        if z_current is None or z_previous is None:
            return self.hold_signal(
                candle=candle,
                symbol="XAUUSD",
                timeframe="M5",
                metadata={"reason": "zero_variance"},
            )

        z_entry = float(p["z_entry"])
        direction: Literal["buy", "sell", "hold"] = "hold"
        # Oversold -> buy; overbought -> sell (position state is the caller's job).
        if z_current <= -z_entry:
            direction = "buy"
        elif z_current >= z_entry:
            direction = "sell"

        confidence = min(1.0, abs(z_current) / (z_entry * 2))
        if direction == "hold" or confidence < float(p["confidence_threshold"]):
            return self.hold_signal(
                candle=candle,
                symbol="XAUUSD",
                timeframe="M5",
                confidence=confidence,
                metadata={"reason": "no_cross", "z_score": round(z_current, 4)},
            )

        band_distance = max(abs(candle.close * float(p["stop_fraction"])), 1e-6)
        if direction == "buy":
            stop_loss = candle.close - band_distance
            take_profit = candle.close + band_distance * float(p["risk_reward"])
        else:
            stop_loss = candle.close + band_distance
            take_profit = candle.close - band_distance * float(p["risk_reward"])

        return self.build_signal(
            candle=candle,
            symbol="XAUUSD",
            timeframe="M5",
            direction=direction,
            entry=candle.close,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            metadata={"z_score": round(z_current, 4)},
        )
