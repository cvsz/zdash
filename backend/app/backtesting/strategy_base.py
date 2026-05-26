from __future__ import annotations

from abc import ABC, abstractmethod
from statistics import mean

from app.backtesting.models import Candle, StrategySignal


class BaseStrategy(ABC):
    name: str = "base"
    default_parameters: dict = {}

    @abstractmethod
    def generate_signal(self, candles: list[Candle], index: int, parameters: dict) -> StrategySignal:
        raise NotImplementedError

    def validate_parameters(self, parameters: dict) -> dict:
        merged = {**self.default_parameters, **(parameters or {})}
        return merged

    def get_description(self) -> str:
        return self.name

    def hold_signal(
        self,
        candle: Candle,
        symbol: str,
        timeframe: str,
        confidence: float = 0.0,
        metadata: dict | None = None,
    ) -> StrategySignal:
        stop_loss = max(candle.close * 0.995, 1e-6)
        take_profit = max(candle.close * 1.005, candle.close + 1e-6)
        return StrategySignal(
            timestamp=candle.timestamp,
            symbol=symbol,
            timeframe=timeframe,
            strategy=self.name,
            direction="hold",
            entry=candle.close,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=max(0.0, min(1.0, confidence)),
            metadata=metadata or {},
        )

    def build_signal(
        self,
        *,
        candle: Candle,
        symbol: str,
        timeframe: str,
        direction: str,
        entry: float,
        stop_loss: float,
        take_profit: float,
        confidence: float,
        metadata: dict | None = None,
    ) -> StrategySignal:
        safe_confidence = max(0.0, min(1.0, confidence))
        if direction == "buy":
            stop_loss = min(stop_loss, entry - 1e-6)
            take_profit = max(take_profit, entry + 1e-6)
        elif direction == "sell":
            stop_loss = max(stop_loss, entry + 1e-6)
            take_profit = min(take_profit, entry - 1e-6)
        else:
            return self.hold_signal(
                candle=candle,
                symbol=symbol,
                timeframe=timeframe,
                confidence=safe_confidence,
                metadata=metadata,
            )

        return StrategySignal(
            timestamp=candle.timestamp,
            symbol=symbol,
            timeframe=timeframe,
            strategy=self.name,
            direction=direction,
            entry=max(entry, 1e-6),
            stop_loss=max(stop_loss, 1e-6),
            take_profit=max(take_profit, 1e-6),
            confidence=safe_confidence,
            metadata=metadata or {},
        )

    @staticmethod
    def volatility(candles: list[Candle]) -> float:
        if not candles:
            return 1e-6
        return max(mean((candle.high - candle.low) for candle in candles), 1e-6)
