from __future__ import annotations

from app.core.config import get_settings
from app.core.events import event_bus
from app.trading.ai_analysis import TradingAIAnalysis
from app.trading.funnel_filter import FunnelFilter
from app.trading.models import Candle, ScannerResult
from app.trading.mt5_adapter import MT5Adapter
from app.trading.signal_validation import SignalValidationService


class XAUScanner:
    def __init__(
        self,
        mt5_adapter: MT5Adapter | None = None,
        funnel_filter: FunnelFilter | None = None,
        ai_analysis: TradingAIAnalysis | None = None,
        validation_service: SignalValidationService | None = None,
    ) -> None:
        self.settings = get_settings()
        self.mt5 = mt5_adapter or MT5Adapter()
        self.filter = funnel_filter or FunnelFilter()
        self.ai = ai_analysis or TradingAIAnalysis()
        self.validation = validation_service or SignalValidationService()

    def scan(self, symbol: str = 'XAUUSD', timeframe: str = 'M5') -> ScannerResult:
        event_bus.emit('trading.scan.started', 'XAUScanner', 'Trading scan started', {'symbol': symbol, 'timeframe': timeframe})
        candles = self.mt5.get_candles(symbol=symbol, timeframe=timeframe, limit=300)
        result = self.scan_with_candles(candles=candles, symbol=symbol, timeframe=timeframe)
        event_bus.emit(
            'trading.scan.completed',
            'XAUScanner',
            'Trading scan completed',
            {'symbol': symbol, 'timeframe': timeframe, 'signal_id': result.latest_signal.id if result.latest_signal else None},
        )
        return result

    def scan_with_candles(self, candles: list[Candle], symbol: str, timeframe: str) -> ScannerResult:
        latest_signal = self.filter.generate_signal(candles=candles, symbol=symbol, timeframe=timeframe)
        event_bus.emit(
            'trading.signal.generated',
            'XAUScanner',
            'Trading signal generated',
            {'signal_id': latest_signal.id, 'direction': latest_signal.direction, 'confidence': latest_signal.confidence},
        )

        ai_summary = self.ai.analyze_scanner_context(candles=candles, signal=latest_signal)
        latest_signal.reason = ai_summary

        validation = self.validation.validate(latest_signal)
        if validation.valid:
            event_bus.emit(
                'trading.signal.validated',
                'SignalValidationService',
                'Signal validated',
                {'signal_id': latest_signal.id, 'warnings': validation.warnings},
            )
        else:
            event_bus.emit(
                'trading.signal.rejected',
                'SignalValidationService',
                'Signal rejected',
                {'signal_id': latest_signal.id, 'reason': validation.reason},
            )

        return ScannerResult(
            symbol=symbol,
            timeframe=timeframe,
            candles_analyzed=len(candles),
            latest_signal=latest_signal,
            validation=validation,
            ai_summary=ai_summary,
        )
