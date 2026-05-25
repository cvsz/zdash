from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.risk.models import AccountSnapshot


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
    entry_zone: tuple[float, float] = (0.0, 0.0)
    stop_loss: float = 0.0
    take_profit: float = 0.0
    confidence: float = 0.0
    strategy: str = 'unknown'
    filter_state: dict[str, Any] = Field(default_factory=dict)
    ai_summary: str = ''
    validation_status: str = 'pending'
    risk_status: str = 'unchecked'
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ExecutionRequest(BaseModel):
    signal: Signal
    lot_size: float = 0.01
    snapshot: AccountSnapshot | None = None
