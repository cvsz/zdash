from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AITraderStrategy:
    id: str
    name: str
    description: str
    risk_profile: str
    min_candles: int
    default_min_confidence: float
    supported_symbols: tuple[str, ...]
    supported_timeframes: tuple[str, ...]
    simulation_only: bool = True

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "risk_profile": self.risk_profile,
            "min_candles": self.min_candles,
            "default_min_confidence": self.default_min_confidence,
            "supported_symbols": list(self.supported_symbols),
            "supported_timeframes": list(self.supported_timeframes),
            "simulation_only": self.simulation_only,
        }


_STRATEGIES: dict[str, AITraderStrategy] = {
    "trend_momentum_v1": AITraderStrategy(
        id="trend_momentum_v1",
        name="Trend Momentum v1",
        description="Follows aligned moving-average trend and short-term momentum.",
        risk_profile="balanced",
        min_candles=21,
        default_min_confidence=0.55,
        supported_symbols=("XAUUSD", "BTCUSD", "ETHUSD", "EURUSD"),
        supported_timeframes=("M5", "M15", "H1"),
    ),
    "mean_reversion_v1": AITraderStrategy(
        id="mean_reversion_v1",
        name="Mean Reversion v1",
        description="Looks for stretched price versus slow moving average with stabilizing momentum.",
        risk_profile="moderate",
        min_candles=21,
        default_min_confidence=0.58,
        supported_symbols=("XAUUSD", "BTCUSD", "ETHUSD", "EURUSD"),
        supported_timeframes=("M5", "M15", "H1"),
    ),
    "volatility_breakout_v1": AITraderStrategy(
        id="volatility_breakout_v1",
        name="Volatility Breakout v1",
        description="Requires elevated volatility and aligned momentum before simulating a breakout signal.",
        risk_profile="aggressive",
        min_candles=28,
        default_min_confidence=0.62,
        supported_symbols=("XAUUSD", "BTCUSD", "ETHUSD"),
        supported_timeframes=("M5", "M15", "H1"),
    ),
    "conservative_guarded_v1": AITraderStrategy(
        id="conservative_guarded_v1",
        name="Conservative Guarded v1",
        description="Uses stricter confidence and volatility filters, preferring hold decisions.",
        risk_profile="conservative",
        min_candles=28,
        default_min_confidence=0.72,
        supported_symbols=("XAUUSD", "EURUSD"),
        supported_timeframes=("M15", "H1", "M5"),
    ),
}


def list_strategies() -> list[AITraderStrategy]:
    return list(_STRATEGIES.values())


def get_strategy(strategy_id: str) -> AITraderStrategy | None:
    return _STRATEGIES.get(strategy_id)


def resolve_strategy(strategy_id: str | None) -> AITraderStrategy:
    if strategy_id and strategy_id in _STRATEGIES:
        return _STRATEGIES[strategy_id]
    return _STRATEGIES["trend_momentum_v1"]
