from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import get_settings
from app.trading.models import SignalValidationResult, TradingSignal


class SignalValidationService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def validate(self, signal: TradingSignal) -> SignalValidationResult:
        warnings: list[str] = []
        problems: list[str] = []

        expected_symbol = self.settings.trading_symbol
        expected_timeframe = self.settings.trading_timeframe

        if signal.symbol.upper() != expected_symbol.upper():
            problems.append(f'symbol must be {expected_symbol}')

        if signal.timeframe.upper() != expected_timeframe.upper():
            problems.append(f'timeframe must be {expected_timeframe}')

        if signal.confidence < 0 or signal.confidence > 1:
            problems.append('confidence must be between 0 and 1')

        if signal.direction not in {'buy', 'sell', 'hold'}:
            problems.append('direction must be one of buy/sell/hold')

        if signal.direction == 'buy' and not (signal.stop_loss < signal.entry < signal.take_profit):
            problems.append('buy signal requires stop_loss < entry < take_profit')

        if signal.direction == 'sell' and not (signal.take_profit < signal.entry < signal.stop_loss):
            problems.append('sell signal requires take_profit < entry < stop_loss')

        if signal.direction == 'hold':
            warnings.append('hold signals are non-executable and should remain dry-run only')

        age_seconds = (datetime.now(timezone.utc) - signal.created_at).total_seconds()
        if age_seconds > self.settings.trading_max_signal_age_seconds:
            problems.append('signal is too old for execution')

        if problems:
            return SignalValidationResult(
                valid=False,
                reason='; '.join(problems),
                warnings=warnings,
                signal=signal,
            )

        return SignalValidationResult(
            valid=True,
            reason='signal is valid for dry-run evaluation',
            warnings=warnings,
            signal=signal,
        )
