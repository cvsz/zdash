from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

RiskLevel = Literal['normal', 'warning', 'danger', 'emergency']


class AccountSnapshot(BaseModel):
    balance: float
    equity: float
    peak_equity: float
    daily_start_equity: float
    open_positions: int = 0
    floating_pnl: float = 0.0
    realized_pnl_today: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DrawdownResult(BaseModel):
    current_equity: float
    peak_equity: float
    daily_start_equity: float
    total_drawdown_percent: float
    daily_drawdown_percent: float
    floating_pnl: float
    risk_level: RiskLevel
    breached: bool
    breach_reason: str | None = None


class HaltState(BaseModel):
    halted: bool = False
    reason: str | None = None
    source: str | None = None
    created_at: datetime | None = None
    resumed_at: datetime | None = None
    resume_reason: str | None = None


class RiskDecision(BaseModel):
    approved: bool
    reason: str
    risk_level: RiskLevel
    halt_active: bool
    drawdown: DrawdownResult | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
