from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import get_settings
from app.core.events import event_bus
from app.risk.guardian_service import get_guardian_service
from app.trading.models import ExecutionRequest, ExecutionResult, TradingSignal
from app.trading.mt5_adapter import MT5Adapter
from app.trading.signal_validation import SignalValidationService


class ExecutionEngine:
    def __init__(
        self,
        validation_service: SignalValidationService | None = None,
        mt5_adapter: MT5Adapter | None = None,
    ) -> None:
        self.settings = get_settings()
        self.validation_service = validation_service or SignalValidationService()
        self.mt5_adapter = mt5_adapter or MT5Adapter()

    @staticmethod
    def _clamp_confidence(value: float) -> float:
        return max(0.0, min(1.0, value))

    def _normalize_signal(self, raw_signal: object) -> TradingSignal:
        if isinstance(raw_signal, TradingSignal):
            return raw_signal

        if hasattr(raw_signal, 'model_dump'):
            payload = raw_signal.model_dump()
        elif isinstance(raw_signal, dict):
            payload = dict(raw_signal)
        else:
            raise ValueError('unsupported signal payload')

        direction = payload.get('direction', 'hold')
        if direction == 'neutral':
            direction = 'hold'

        entry = payload.get('entry')
        entry_zone = payload.get('entry_zone')
        if entry is None:
            if isinstance(entry_zone, (list, tuple)) and len(entry_zone) == 2:
                low, high = entry_zone
                if isinstance(low, (int, float)) and isinstance(high, (int, float)):
                    entry = float((low + high) / 2)
        if not isinstance(entry, (int, float)) or entry <= 0:
            entry = 2350.0

        stop_loss = payload.get('stop_loss')
        take_profit = payload.get('take_profit')
        if not isinstance(stop_loss, (int, float)) or stop_loss <= 0:
            stop_loss = entry - 1.5 if direction == 'buy' else (entry + 1.5 if direction == 'sell' else entry)
        if not isinstance(take_profit, (int, float)) or take_profit <= 0:
            take_profit = entry + 3.0 if direction == 'buy' else (entry - 3.0 if direction == 'sell' else entry)

        created_at = payload.get('created_at')
        if not created_at:
            created_at = datetime.now(timezone.utc)

        return TradingSignal(
            id=str(payload.get('id') or uuid4()),
            symbol=str(payload.get('symbol') or self.settings.trading_symbol),
            timeframe=str(payload.get('timeframe') or self.settings.trading_timeframe),
            direction=direction,
            strategy=str(payload.get('strategy') or self.settings.trading_default_strategy),
            confidence=self._clamp_confidence(float(payload.get('confidence', 0.5))),
            entry=float(entry),
            stop_loss=float(stop_loss),
            take_profit=float(take_profit),
            reason=str(payload.get('reason') or payload.get('ai_summary') or 'Normalized legacy signal for dry-run execution.'),
            metadata=payload.get('metadata') or {'legacy_payload': payload},
            created_at=created_at,
        )

    @staticmethod
    def _as_execution_request(request: object) -> tuple[TradingSignal, bool, object | None]:
        if isinstance(request, ExecutionRequest):
            return request.signal, request.dry_run, None

        if hasattr(request, 'signal'):
            signal = getattr(request, 'signal')
            dry_run = getattr(request, 'dry_run', True)
            snapshot = getattr(request, 'snapshot', None)
            return signal, bool(dry_run), snapshot

        if isinstance(request, dict):
            signal = request.get('signal')
            dry_run = request.get('dry_run', True)
            snapshot = request.get('snapshot')
            return signal, bool(dry_run), snapshot

        raise ValueError('unsupported execution request')

    def execute(self, request: object) -> ExecutionResult:
        raw_signal, request_dry_run, snapshot = self._as_execution_request(request)
        signal = self._normalize_signal(raw_signal)

        if snapshot is not None:
            decision = get_guardian_service().approve_execution(signal=signal.model_dump(mode='json'), snapshot=snapshot)
            if not decision.approved or decision.halt_active:
                event_bus.emit(
                    'trading.execution.blocked',
                    'ExecutionEngine',
                    'Execution blocked by risk guardian',
                    {'signal_id': signal.id, 'reason': decision.reason},
                )
                return ExecutionResult(
                    ok=False,
                    status='blocked_by_risk',
                    dry_run=True,
                    signal=signal,
                    message=decision.reason,
                )

        validation = self.validation_service.validate(signal)
        if not validation.valid:
            event_bus.emit(
                'trading.execution.blocked',
                'ExecutionEngine',
                'Execution blocked by validation',
                {'signal_id': signal.id, 'reason': validation.reason},
            )
            return ExecutionResult(
                ok=False,
                status='blocked_by_validation',
                dry_run=True,
                signal=signal,
                message=validation.reason,
            )

        if signal.direction == 'hold':
            message = 'Hold signals are not executable in Phase 02.'
            event_bus.emit(
                'trading.execution.blocked',
                'ExecutionEngine',
                message,
                {'signal_id': signal.id},
            )
            return ExecutionResult(
                ok=False,
                status='blocked_by_validation',
                dry_run=True,
                signal=signal,
                message=message,
            )

        effective_dry_run = request_dry_run or self.settings.dry_run
        if effective_dry_run:
            result = ExecutionResult(
                ok=True,
                status='simulated',
                dry_run=True,
                signal=signal,
                message='Dry-run execution simulated successfully.',
                simulated_order_id=f'sim-{uuid4()}',
            )
            event_bus.emit(
                'trading.execution.simulated',
                'ExecutionEngine',
                result.message,
                {'signal_id': signal.id, 'simulated_order_id': result.simulated_order_id},
            )
            return result

        if not self.settings.live_trading_ack:
            message = 'LIVE_TRADING_ACK=false blocks non-dry-run execution.'
            event_bus.emit(
                'trading.execution.blocked',
                'ExecutionEngine',
                message,
                {'signal_id': signal.id},
            )
            return ExecutionResult(
                ok=False,
                status='blocked_by_config',
                dry_run=False,
                signal=signal,
                message=message,
            )

        result = self.mt5_adapter.send_order(signal)
        if result.status == 'simulated':
            event_bus.emit(
                'trading.execution.simulated',
                'ExecutionEngine',
                result.message,
                {'signal_id': signal.id, 'simulated_order_id': result.simulated_order_id},
            )
            return result

        event_bus.emit(
            'trading.execution.failed' if result.status == 'failed' else 'trading.execution.blocked',
            'ExecutionEngine',
            result.message,
            {'signal_id': signal.id, 'status': result.status},
        )
        return result
