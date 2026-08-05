"""Trading core package for Phase 02 dry-run foundation."""

from app.trading.execution_engine import ExecutionEngine
from app.trading.funnel_filter import FunnelFilter
from app.trading.models import (
    Candle,
    ExecutionRequest,
    ExecutionResult,
    ScannerResult,
    SignalValidationResult,
    TradingSignal,
)
from app.trading.mt5_adapter import MT5Adapter
from app.trading.trading_service import TradingService
from app.trading.xau_scanner import XAUScanner

__all__ = [
    "Candle",
    "ExecutionEngine",
    "ExecutionRequest",
    "ExecutionResult",
    "FunnelFilter",
    "MT5Adapter",
    "ScannerResult",
    "SignalValidationResult",
    "TradingService",
    "TradingSignal",
    "XAUScanner",
]
