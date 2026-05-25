from __future__ import annotations

from app.backtesting.models import Candle, StrategySignal
from app.backtesting.strategy_base import BaseStrategy


class OBAggressiveStrategy(BaseStrategy):
    name = "ob_aggressive"
    default_parameters = {"lookback": 12, "risk_reward": 2.0, "confidence_threshold": 0.55, "atr_multiplier": 1.2}

    def generate_signal(self, candles: list[Candle], index: int, parameters: dict) -> StrategySignal:
        p = self.validate_parameters(parameters)
        c = candles[index]
        if index < p["lookback"]:
            return StrategySignal(timestamp=c.timestamp, symbol="XAUUSD", timeframe="M5", strategy=self.name, direction="hold", entry=c.close, stop_loss=c.close*0.99, take_profit=c.close*1.01, confidence=0)
        window = candles[index - p["lookback"]:index]
        hi, lo = max(x.high for x in window), min(x.low for x in window)
        atr = sum(x.high - x.low for x in window) / len(window)
        conf = min(1.0, 0.5 + abs(c.close - window[-1].close) / max(atr, 1e-6))
        direction = "hold"
        if c.close > hi and conf >= p["confidence_threshold"]:
            direction = "buy"
        elif c.close < lo and conf >= p["confidence_threshold"]:
            direction = "sell"
        sl_dist = atr * p["atr_multiplier"]
        sl = c.close - sl_dist if direction != "sell" else c.close + sl_dist
        tp = c.close + sl_dist * p["risk_reward"] if direction != "sell" else c.close - sl_dist * p["risk_reward"]
        return StrategySignal(timestamp=c.timestamp, symbol="XAUUSD", timeframe="M5", strategy=self.name, direction=direction, entry=c.close, stop_loss=sl, take_profit=tp, confidence=min(1.0, max(0.0, conf)))
