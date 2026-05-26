from __future__ import annotations

from app.trading.models import TradingSignal
from app.trading.risk_models import Signal as LegacySignal
from app.trading.xau_scanner import XAUScanner as CoreXAUScanner


class XAUScanner:
    """
    Backward-compatible scanner wrapper.

    Legacy callers expect `scan()` to return a `risk_models.Signal`. Phase 02
    core uses `xau_scanner.XAUScanner` and `TradingSignal`.
    """

    def __init__(self, mt5=None) -> None:
        self._core = CoreXAUScanner(mt5_adapter=mt5)

    @staticmethod
    def _to_legacy(signal: TradingSignal) -> LegacySignal:
        entry_low = signal.entry - 0.1
        entry_high = signal.entry + 0.1
        return LegacySignal(
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            direction='neutral' if signal.direction == 'hold' else signal.direction,
            entry_zone=(round(entry_low, 4), round(entry_high, 4)),
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            confidence=signal.confidence,
            strategy=signal.strategy,
            filter_state=signal.metadata.get('funnel_state', {}),
            ai_summary=signal.reason,
        )

    def scan(self) -> LegacySignal:
        result = self._core.scan()
        if result.latest_signal is None:
            raise RuntimeError('scanner did not generate a signal')
        return self._to_legacy(result.latest_signal)
