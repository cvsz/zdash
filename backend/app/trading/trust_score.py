from __future__ import annotations

from pydantic import BaseModel, Field


class TrustScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    reconciliation_health: float = Field(ge=0.0, le=1.0)
    regime_stability: float = Field(ge=0.0, le=1.0)


class TrustScoreEngine:
    """Financial trust score from reconciliation health and regime stability.

    Weights follow the zeaz-platform reference: 60% reconciliation,
    40% regime stability.
    """

    RECONCILIATION_WEIGHT = 0.6
    REGIME_STABILITY_WEIGHT = 0.4

    def __init__(self) -> None:
        self.score = 1.0

    def calculate_score(
        self,
        reconciliation_health: float,
        regime_stability: float,
    ) -> TrustScore:
        if not 0.0 <= reconciliation_health <= 1.0:
            raise ValueError("reconciliation_health must be within [0, 1]")
        if not 0.0 <= regime_stability <= 1.0:
            raise ValueError("regime_stability must be within [0, 1]")

        self.score = round(
            (
                reconciliation_health * self.RECONCILIATION_WEIGHT
                + regime_stability * self.REGIME_STABILITY_WEIGHT
            ),
            4,
        )
        return TrustScore(
            score=self.score,
            reconciliation_health=reconciliation_health,
            regime_stability=regime_stability,
        )
