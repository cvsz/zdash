from __future__ import annotations

from app.trading.models import TradingSignal
from app.trading.risk_models import Signal as LegacySignal
from app.trading.signal_validation import SignalValidationService


class SignalValidator:
    """Backward-compatible validator wrapper returning legacy dict payloads."""

    def __init__(self) -> None:
        self._service = SignalValidationService()

    @staticmethod
    def _normalize(signal: LegacySignal | TradingSignal) -> TradingSignal:
        if isinstance(signal, TradingSignal):
            return signal

        entry = (signal.entry_zone[0] + signal.entry_zone[1]) / 2 if signal.entry_zone else 2350.0
        direction = 'hold' if signal.direction == 'neutral' else signal.direction
        return TradingSignal(
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            direction=direction,
            strategy=signal.strategy,
            confidence=max(0.0, min(1.0, signal.confidence)),
            entry=entry,
            stop_loss=signal.stop_loss if signal.stop_loss > 0 else entry,
            take_profit=signal.take_profit if signal.take_profit > 0 else entry,
            reason=signal.ai_summary or 'Legacy validation request',
            metadata={'legacy_filter_state': signal.filter_state},
        )

    def validate(self, signal: LegacySignal | TradingSignal) -> dict:
        normalized = self._normalize(signal)
        result = self._service.validate(normalized)
        issues: list[str] = []
        if not result.valid:
            issues.append(result.reason)
        return {
            'valid': result.valid,
            'issues': issues,
            'warnings': result.warnings,
            'signal_id': normalized.id,
        }
