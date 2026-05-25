from __future__ import annotations

from app.backtesting.models import Candle, StrategySignal
from app.backtesting.strategy_base import BaseStrategy


class TrendFollowStrategy(BaseStrategy):
    name = "trend_follow"
    default_parameters = {"short_window": 10, "long_window": 30, "risk_reward": 1.5, "confidence_threshold": 0.6, "atr_multiplier": 1.5}

    def validate_parameters(self, parameters: dict) -> dict:
        p = super().validate_parameters(parameters)
        if p["short_window"] >= p["long_window"]:
            raise ValueError("short_window must be less than long_window")
        return p

    def generate_signal(self, candles: list[Candle], index: int, parameters: dict) -> StrategySignal:
        p = self.validate_parameters(parameters)
        c = candles[index]
        if index < p["long_window"]:
            return StrategySignal(timestamp=c.timestamp, symbol="XAUUSD", timeframe="M5", strategy=self.name, direction="hold", entry=c.close, stop_loss=c.close*0.99, take_profit=c.close*1.01, confidence=0)
        closes = [x.close for x in candles]
        sma_s = sum(closes[index-p["short_window"]+1:index+1]) / p["short_window"]
        sma_l = sum(closes[index-p["long_window"]+1:index+1]) / p["long_window"]
        prev_s = sum(closes[index-p["short_window"]:index]) / p["short_window"]
        prev_l = sum(closes[index-p["long_window"]:index]) / p["long_window"]
        direction = "hold"
        if prev_s <= prev_l and sma_s > sma_l:
            direction = "buy"
        elif prev_s >= prev_l and sma_s < sma_l:
            direction = "sell"
        atr = sum((x.high - x.low) for x in candles[index-10:index]) / 10
        conf = min(1.0, max(0.0, abs(sma_s - sma_l) / max(atr, 1e-6)))
        sl_dist = atr * p["atr_multiplier"]
        sl = c.close - sl_dist if direction != "sell" else c.close + sl_dist
        tp = c.close + sl_dist * p["risk_reward"] if direction != "sell" else c.close - sl_dist * p["risk_reward"]
        return StrategySignal(timestamp=c.timestamp, symbol="XAUUSD", timeframe="M5", strategy=self.name, direction=direction, entry=c.close, stop_loss=sl, take_profit=tp, confidence=conf)
