from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class Candle(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


class Signal(BaseModel):
    symbol: str
    timeframe: str
    direction: Literal['buy', 'sell', 'neutral']
    entry_zone: tuple[float, float]
    stop_loss: float
    take_profit: float
    confidence: float
    strategy: str
    filter_state: dict
    ai_summary: str = ''
    validation_status: str = 'pending'
    risk_status: str = 'unchecked'
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ExecutionRequest(BaseModel):
    signal: Signal
    lot_size: float = 0.01
