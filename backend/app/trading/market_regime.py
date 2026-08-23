from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

MarketRegime = Literal[
    "normal",
    "volatile",
    "crisis",
    "illiquid",
    "exchange_unstable",
    "black_swan",
]

VOLATILE_THRESHOLD = 0.5
CRISIS_THRESHOLD = 0.8
ILLIQUID_DEPTH_THRESHOLD = 0.2


class RegimeAssessment(BaseModel):
    regime: MarketRegime
    volatility_index: float = Field(ge=0.0, le=1.0)
    liquidity_depth: float = Field(ge=0.0, le=1.0)


class MarketRegimeEngine:
    """Classifies current market conditions from volatility and liquidity inputs."""

    def __init__(self) -> None:
        self.current_regime: MarketRegime = "normal"

    def assess_regime(
        self,
        volatility_index: float,
        liquidity_depth: float,
        exchange_stable: bool = True,
    ) -> RegimeAssessment:
        if not 0.0 <= volatility_index <= 1.0:
            raise ValueError("volatility_index must be within [0, 1]")
        if not 0.0 <= liquidity_depth <= 1.0:
            raise ValueError("liquidity_depth must be within [0, 1]")

        # Fail closed: unstable exchange or thin book outranks volatility signals.
        if not exchange_stable:
            regime: MarketRegime = "exchange_unstable"
        elif liquidity_depth < ILLIQUID_DEPTH_THRESHOLD:
            regime = "illiquid"
        elif volatility_index > CRISIS_THRESHOLD:
            regime = "crisis"
        elif volatility_index > VOLATILE_THRESHOLD:
            regime = "volatile"
        else:
            regime = "normal"

        self.current_regime = regime
        return RegimeAssessment(
            regime=regime,
            volatility_index=volatility_index,
            liquidity_depth=liquidity_depth,
        )
