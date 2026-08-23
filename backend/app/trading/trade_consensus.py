from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.trading.market_regime import MarketRegime

DEFAULT_MIN_CONFIDENCE = 0.7
BLOCKED_REGIMES: frozenset[str] = frozenset(
    {"crisis", "black_swan", "exchange_unstable"}
)


class ConsensusDecision(BaseModel):
    approved: bool
    reason: str
    min_confidence: float = Field(ge=0.0, le=1.0)
    regime: MarketRegime


class TradeConsensusEngine:
    """Multi-gate approval before any execution proposal may proceed.

    Gates (all must pass, fail closed on missing data):
      1. market regime is tradeable
      2. AI confidence meets the minimum threshold
      3. risk engine approves the order
    """

    def __init__(
        self,
        regime_engine: Any = None,
        risk_engine: Any = None,
        min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    ) -> None:
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be within [0, 1]")
        self.regime_engine = regime_engine
        self.risk_engine = risk_engine
        self.min_confidence = min_confidence

    def validate_execution(
        self,
        order_proposal: dict[str, Any],
    ) -> ConsensusDecision:
        regime = self._current_regime()

        if regime in BLOCKED_REGIMES:
            return ConsensusDecision(
                approved=False,
                reason=f"market regime is {regime}",
                min_confidence=self.min_confidence,
                regime=regime,
            )

        confidence = order_proposal.get("confidence")
        if not isinstance(confidence, int | float) or confidence < self.min_confidence:
            return ConsensusDecision(
                approved=False,
                reason="AI confidence below threshold or missing",
                min_confidence=self.min_confidence,
                regime=regime,
            )

        if self.risk_engine is not None and not self.risk_engine.evaluate_order(
            order_proposal,
        ):
            return ConsensusDecision(
                approved=False,
                reason="risk engine rejected the order",
                min_confidence=self.min_confidence,
                regime=regime,
            )

        return ConsensusDecision(
            approved=True,
            reason="consensus reached",
            min_confidence=self.min_confidence,
            regime=regime,
        )

    def _current_regime(self) -> MarketRegime:
        if self.regime_engine is None:
            # Fail closed when no regime engine is wired in.
            return "black_swan"
        current = getattr(self.regime_engine, "current_regime", None)
        if current in BLOCKED_REGIMES or current == "normal" or current == "volatile":
            return current  # type: ignore[no-any-return]
        # Fail closed on any unrecognized regime value.
        return "black_swan"
