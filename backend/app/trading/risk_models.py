from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.risk.models import AccountSnapshot
from app.trading.models import Candle as TradingCandle
from app.trading.models import ExecutionRequest as TradingExecutionRequest
from app.trading.models import TradingSignal


class Candle(TradingCandle):
    """Legacy alias for phase-02 Candle model."""


class Signal(BaseModel):
    symbol: str
    timeframe: str
    direction: Literal["buy", "sell", "neutral"]
    entry_zone: tuple[float, float] = (0.0, 0.0)
    stop_loss: float = 0.0
    take_profit: float = 0.0
    confidence: float = 0.0
    strategy: str = "unknown"
    filter_state: dict[str, Any] = Field(default_factory=dict)
    ai_summary: str = ""
    validation_status: str = "pending"
    risk_status: str = "unchecked"
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_trading_signal(self) -> TradingSignal:
        entry = (
            (self.entry_zone[0] + self.entry_zone[1]) / 2 if self.entry_zone else 2350.0
        )
        direction = "hold" if self.direction == "neutral" else self.direction

        stop_loss = self.stop_loss
        take_profit = self.take_profit
        if stop_loss <= 0:
            stop_loss = (
                entry - 1.5
                if direction == "buy"
                else (entry + 1.5 if direction == "sell" else entry)
            )
        if take_profit <= 0:
            take_profit = (
                entry + 3.0
                if direction == "buy"
                else (entry - 3.0 if direction == "sell" else entry)
            )

        return TradingSignal(
            symbol=self.symbol,
            timeframe=self.timeframe,
            direction=direction,
            strategy=self.strategy,
            confidence=max(0.0, min(1.0, self.confidence)),
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason=self.ai_summary or "Legacy signal conversion",
            metadata={
                "filter_state": self.filter_state,
                "validation_status": self.validation_status,
                "risk_status": self.risk_status,
            },
            created_at=self.created_at,
        )


class ExecutionRequest(BaseModel):
    signal: Signal | TradingSignal
    lot_size: float = 0.01
    snapshot: AccountSnapshot | None = None
    dry_run: bool = True
    confirmation: bool = False

    def to_phase2_request(self) -> TradingExecutionRequest:
        signal = (
            self.signal.to_trading_signal()
            if isinstance(self.signal, Signal)
            else self.signal
        )
        return TradingExecutionRequest(
            signal=signal, dry_run=self.dry_run, confirmation=self.confirmation
        )
