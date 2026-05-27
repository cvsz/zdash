from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0

    @field_validator("open", "high", "low", "close")
    @classmethod
    def _positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("OHLC values must be positive")
        return v

    @field_validator("volume")
    @classmethod
    def _volume_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("volume must be non-negative")
        return v

    @model_validator(mode="after")
    def _validate_ranges(self) -> "Candle":
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be >= open/close/low")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be <= open/close/high")
        return self


class StrategySignal(BaseModel):
    timestamp: datetime
    symbol: str
    timeframe: str
    strategy: str
    direction: Literal["buy", "sell", "hold"]
    entry: float
    stop_loss: float
    take_profit: float
    confidence: float
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("confidence")
    @classmethod
    def _confidence_range(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("confidence must be in [0,1]")
        return v

    @field_validator("entry", "stop_loss", "take_profit")
    @classmethod
    def _price_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price fields must be positive")
        return v

    @model_validator(mode="after")
    def _validate_directional_levels(self) -> "StrategySignal":
        if self.direction == "buy":
            if not (self.stop_loss < self.entry < self.take_profit):
                raise ValueError("buy signals require stop_loss < entry < take_profit")
        elif self.direction == "sell":
            if not (self.take_profit < self.entry < self.stop_loss):
                raise ValueError("sell signals require take_profit < entry < stop_loss")
        return self


class SimulatedTrade(BaseModel):
    id: str
    symbol: str
    timeframe: str
    strategy: str
    direction: Literal["buy", "sell", "hold"]
    entry_time: datetime
    exit_time: datetime | None = None
    entry_price: float
    exit_price: float | None = None
    stop_loss: float
    take_profit: float
    size: float
    pnl: float = 0
    pnl_percent: float = 0
    rr: float = 0
    status: Literal["open", "closed", "skipped"]
    exit_reason: (
        Literal[
            "take_profit", "stop_loss", "signal_exit", "end_of_data", "invalid_signal"
        ]
        | None
    ) = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BacktestRequest(BaseModel):
    strategy: str
    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    dataset: str = "mock"
    initial_balance: float = 10000
    risk_per_trade_percent: float = 1
    commission_per_trade: float = 0
    spread_points: float = 25
    slippage_points: float = 5
    parameters: dict[str, Any] = Field(default_factory=dict)

    @field_validator("initial_balance")
    @classmethod
    def _initial_balance_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("initial_balance must be > 0")
        return v

    @field_validator("risk_per_trade_percent")
    @classmethod
    def _risk_percent_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("risk_per_trade_percent must be > 0")
        return v

    @field_validator("commission_per_trade", "spread_points", "slippage_points")
    @classmethod
    def _non_negative_costs(cls, v: float) -> float:
        if v < 0:
            raise ValueError("cost-related values must be >= 0")
        return v


class BacktestMetrics(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    gross_profit: float
    gross_loss: float
    net_profit: float
    net_profit_percent: float
    profit_factor: float
    max_drawdown_percent: float
    average_rr: float
    expectancy: float
    sharpe_like_score: float
    consecutive_losses: int
    monthly_return_table: dict[str, float]


class BacktestResult(BaseModel):
    id: str
    request: BacktestRequest
    strategy: str
    symbol: str
    timeframe: str
    initial_balance: float
    final_balance: float
    metrics: BacktestMetrics
    trades: list[SimulatedTrade]
    parameters: dict[str, Any]
    started_at: datetime
    finished_at: datetime
    duration_ms: int
    warnings: list[str] = Field(default_factory=list)


class OptimizationRequest(BaseModel):
    strategy: str
    symbol: str = "XAUUSD"
    timeframe: str = "M5"
    dataset: str = "mock"
    initial_balance: float = 10000
    parameter_grid: dict[str, list[Any]]
    sort_metric: str = "profit_factor"
    max_combinations: int = 100

    @field_validator("max_combinations")
    @classmethod
    def _max_combinations_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("max_combinations must be > 0")
        return v


class OptimizationResult(BaseModel):
    id: str
    request: OptimizationRequest
    ranked_results: list[BacktestResult]
    best_result: BacktestResult | None
    sort_metric: str
    total_combinations: int
    executed_combinations: int
    started_at: datetime
    finished_at: datetime
    duration_ms: int
    warnings: list[str] = Field(default_factory=list)


class StrategyPromotionDecision(BaseModel):
    strategy: str
    approved: bool
    reason: str
    metrics: BacktestMetrics | None
    gates: dict[str, bool]
    timestamp: datetime
