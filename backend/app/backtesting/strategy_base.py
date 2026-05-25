from __future__ import annotations

from abc import ABC, abstractmethod

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
