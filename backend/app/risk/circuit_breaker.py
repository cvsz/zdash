from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Literal

from pydantic import BaseModel, Field

from app.risk.halt_flag import HaltFlagStore

DEFAULT_MAX_CONSECUTIVE_LOSSES = 5
DEFAULT_COOLDOWN_MINUTES = 60
DEFAULT_MAX_TRADES_PER_HOUR = 20


class CircuitBreakerStatus(BaseModel):
    is_tripped: bool
    consecutive_losses: int = Field(ge=0)
    max_consecutive_losses: int = Field(ge=1)
    tripped_until: datetime | None = None
    trades_last_hour: int = Field(ge=0)
    max_trades_per_hour: int = Field(ge=1)


class TradeDecision(BaseModel):
    allowed: bool
    reason: Literal[
        "ok",
        "circuit_tripped",
        "rate_limit_exceeded",
    ]


class CircuitBreaker:
    """Halts trading after consecutive losses or excessive trade frequency.

    Complements the drawdown KillSwitch: when tripped it records a halt flag
    through the existing HaltFlagStore so downstream fail-closed checks observe
    a single source of truth.
    """

    def __init__(
        self,
        halt_store: HaltFlagStore | None = None,
        max_consecutive_losses: int = DEFAULT_MAX_CONSECUTIVE_LOSSES,
        cooldown_minutes: int = DEFAULT_COOLDOWN_MINUTES,
        max_trades_per_hour: int = DEFAULT_MAX_TRADES_PER_HOUR,
    ) -> None:
        if max_consecutive_losses < 1:
            raise ValueError("max_consecutive_losses must be >= 1")
        if cooldown_minutes < 1:
            raise ValueError("cooldown_minutes must be >= 1")
        if max_trades_per_hour < 1:
            raise ValueError("max_trades_per_hour must be >= 1")

        self.halt_store = halt_store
        self.max_consecutive_losses = max_consecutive_losses
        self.cooldown_minutes = cooldown_minutes
        self.max_trades_per_hour = max_trades_per_hour

        self.consecutive_losses = 0
        self.tripped_until: datetime | None = None
        self.recent_trades: list[datetime] = []

    def record_trade_outcome(
        self,
        pnl: float,
        now: datetime | None = None,
    ) -> bool:
        """Record a completed trade; returns True if this outcome tripped the breaker."""
        current = now or datetime.now(UTC)
        self._prune_trades(current)

        if pnl > 0:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1

        self.recent_trades.append(current)

        if (
            self.tripped_until is None
            and self.consecutive_losses >= self.max_consecutive_losses
        ):
            self.trip(current)
            return True
        return False

    def trip(self, now: datetime | None = None) -> None:
        current = now or datetime.now(UTC)
        self.tripped_until = current + timedelta(minutes=self.cooldown_minutes)
        if self.halt_store is not None:
            self.halt_store.halt(
                reason=(
                    f"circuit breaker tripped after {self.consecutive_losses} "
                    "consecutive losses"
                ),
                source="circuit_breaker",
            )

    def is_tripped(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(UTC)
        if self.tripped_until is None:
            return False
        if current < self.tripped_until:
            return True
        # Cooldown elapsed: auto-reset.
        self.tripped_until = None
        self.consecutive_losses = 0
        return False

    def check_trade_rate_limit(self, now: datetime | None = None) -> bool:
        """Returns True when the hourly trade allowance is exhausted."""
        current = now or datetime.now(UTC)
        self._prune_trades(current)
        return len(self.recent_trades) >= self.max_trades_per_hour

    def evaluate(self, now: datetime | None = None) -> TradeDecision:
        """Pre-trade check combining trip status and rate limit."""
        current = now or datetime.now(UTC)
        if self.is_tripped(current):
            return TradeDecision(
                allowed=False,
                reason="circuit_tripped",
            )
        if self.check_trade_rate_limit(current):
            return TradeDecision(
                allowed=False,
                reason="rate_limit_exceeded",
            )
        return TradeDecision(allowed=True, reason="ok")

    def get_status(self, now: datetime | None = None) -> CircuitBreakerStatus:
        current = now or datetime.now(UTC)
        self._prune_trades(current)
        return CircuitBreakerStatus(
            is_tripped=self.is_tripped(current),
            consecutive_losses=self.consecutive_losses,
            max_consecutive_losses=self.max_consecutive_losses,
            tripped_until=self.tripped_until,
            trades_last_hour=len(self.recent_trades),
            max_trades_per_hour=self.max_trades_per_hour,
        )

    def _prune_trades(self, current: datetime) -> None:
        cutoff = current - timedelta(hours=1)
        self.recent_trades = [t for t in self.recent_trades if t > cutoff]
