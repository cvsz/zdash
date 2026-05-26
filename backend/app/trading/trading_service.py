from __future__ import annotations

from app.core.config import get_settings
from app.trading.execution_engine import ExecutionEngine
from app.trading.models import ExecutionRequest, ExecutionResult, ScannerResult, SignalValidationResult, TradingSignal
from app.trading.mt5_adapter import MT5Adapter
from app.trading.signal_validation import SignalValidationService
from app.trading.xau_scanner import XAUScanner


class TradingService:
    def __init__(
        self,
        mt5_adapter: MT5Adapter | None = None,
        scanner: XAUScanner | None = None,
        validation_service: SignalValidationService | None = None,
        execution_engine: ExecutionEngine | None = None,
    ) -> None:
        self.settings = get_settings()
        self.mt5 = mt5_adapter or MT5Adapter()
        self.scanner = scanner or XAUScanner(mt5_adapter=self.mt5)
        self.validation_service = validation_service or SignalValidationService()
        self.execution_engine = execution_engine or ExecutionEngine(
            validation_service=self.validation_service,
            mt5_adapter=self.mt5,
        )

    def get_status(self) -> dict:
        return {
            'enabled': self.settings.trading_enabled,
            'dry_run': self.settings.dry_run,
            'live_trading_ack': self.settings.live_trading_ack,
            'mt5_enabled': self.settings.mt5_enabled,
            'default_symbol': self.settings.trading_symbol,
            'default_timeframe': self.settings.trading_timeframe,
        }

    def scan_xau(self, symbol: str = 'XAUUSD', timeframe: str = 'M5') -> ScannerResult:
        return self.scanner.scan(symbol=symbol, timeframe=timeframe)

    def validate_signal(self, signal: TradingSignal) -> SignalValidationResult:
        return self.validation_service.validate(signal)

    def dry_run_execute(self, signal: TradingSignal) -> ExecutionResult:
        request = ExecutionRequest(signal=signal, dry_run=True, confirmation=False)
        return self.execution_engine.execute(request)
