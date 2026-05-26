from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from app.risk.models import RiskDecision


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    @field_validator('open', 'high', 'low', 'close')
    @classmethod
    def _positive_price(cls, value: float) -> float:
        if value <= 0:
            raise ValueError('price fields must be positive')
        return value

    @model_validator(mode='after')
    def _bounds_are_valid(self) -> 'Candle':
        if self.high < max(self.open, self.close, self.low):
            raise ValueError('high must be >= open/close/low')
        if self.low > min(self.open, self.close, self.high):
            raise ValueError('low must be <= open/close/high')
        return self


class TradingSignal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    symbol: str
    timeframe: str
    direction: Literal['buy', 'sell', 'hold']
    strategy: str
    confidence: float
    entry: float
    stop_loss: float
    take_profit: float
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator('confidence')
    @classmethod
    def _confidence_range(cls, value: float) -> float:
        if value < 0 or value > 1:
            raise ValueError('confidence must be between 0 and 1')
        return value


class SignalValidationResult(BaseModel):
    valid: bool
    reason: str
    warnings: list[str] = Field(default_factory=list)
    signal: TradingSignal | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


ExecutionStatus = Literal[
    'simulated',
    'executed',
    'blocked_by_config',
    'blocked_by_validation',
    'blocked_by_risk',
    'failed',
]


class ExecutionRequest(BaseModel):
    signal: TradingSignal
    dry_run: bool = True
    confirmation: bool = False


class ExecutionResult(BaseModel):
    ok: bool
    status: ExecutionStatus
    dry_run: bool
    signal: TradingSignal
    message: str
    risk_decision: RiskDecision | None = None
    simulated_order_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScannerResult(BaseModel):
    symbol: str
    timeframe: str
    candles_analyzed: int
    latest_signal: TradingSignal | None
    validation: SignalValidationResult | None
    ai_summary: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
