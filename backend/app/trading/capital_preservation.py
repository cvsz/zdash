from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.trading.market_regime import MarketRegime

# Drawdown thresholds use the percent scale (0-100) matching DrawdownGuard.
DRAWDOWN_CONTRACTION_PERCENT = 10.0
CONTRACTION_FACTOR = 0.5
CRISIS_EXPOSURE_FLOOR = 0.05

CrisisRegimes: frozenset[str] = frozenset({"crisis", "black_swan", "exchange_unstable"})


class ExposureDecision(BaseModel):
    max_exposure: float = Field(ge=0.0, le=1.0)
    recent_drawdown_percent: float
    regime: MarketRegime
    reason: Literal[
        "full_exposure",
        "drawdown_contraction",
        "crisis_floor",
    ]


class CapitalPreservationGovernor:
    """Contracts allowed exposure as drawdown grows or conditions deteriorate."""

    def __init__(self, max_exposure: float = 1.0) -> None:
        if not 0.0 < max_exposure <= 1.0:
            raise ValueError("max_exposure must be within (0, 1]")
        self.max_exposure = max_exposure

    def adjust_exposure(
        self,
        recent_drawdown_percent: float,
        regime: MarketRegime,
    ) -> ExposureDecision:
        if recent_drawdown_percent < 0.0:
            raise ValueError("recent_drawdown_percent must be non-negative")

        if recent_drawdown_percent > DRAWDOWN_CONTRACTION_PERCENT:
            self.max_exposure *= CONTRACTION_FACTOR
            return ExposureDecision(
                max_exposure=self.max_exposure,
                recent_drawdown_percent=recent_drawdown_percent,
                regime=regime,
                reason="drawdown_contraction",
            )

        if regime in CrisisRegimes:
            self.max_exposure = CRISIS_EXPOSURE_FLOOR
            return ExposureDecision(
                max_exposure=self.max_exposure,
                recent_drawdown_percent=recent_drawdown_percent,
                regime=regime,
                reason="crisis_floor",
            )

        self.max_exposure = 1.0
        return ExposureDecision(
            max_exposure=self.max_exposure,
            recent_drawdown_percent=recent_drawdown_percent,
            regime=regime,
            reason="full_exposure",
        )
