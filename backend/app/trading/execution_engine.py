from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.core.config import get_settings
from app.core.events import event_bus
from app.risk.guardian_service import get_guardian_service
from app.risk.models import AccountSnapshot, RiskDecision
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

    def _resolve_snapshot(self, provided_snapshot: object | None) -> AccountSnapshot:
        if provided_snapshot is not None:
            return AccountSnapshot.model_validate(provided_snapshot)

        raw_snapshot = self.mt5_adapter.get_account_snapshot()
        if not isinstance(raw_snapshot, dict):
            raise ValueError('MT5 adapter returned an invalid account snapshot payload.')

        balance = float(raw_snapshot.get('balance', 10000.0))
        equity = float(raw_snapshot.get('equity', balance))
        peak_equity = float(raw_snapshot.get('peak_equity', max(balance, equity)))
        daily_start_equity = float(raw_snapshot.get('daily_start_equity', balance))

        open_positions_raw = raw_snapshot.get('open_positions', 0)
        try:
            open_positions = int(open_positions_raw)
        except (TypeError, ValueError):
            open_positions = 0

        floating_pnl = float(raw_snapshot.get('floating_pnl', equity - balance))
        realized_pnl_today = float(raw_snapshot.get('realized_pnl_today', 0.0))

        payload: dict[str, Any] = {
            'balance': balance,
            'equity': equity,
            'peak_equity': peak_equity,
            'daily_start_equity': daily_start_equity,
            'open_positions': open_positions,
            'floating_pnl': floating_pnl,
            'realized_pnl_today': realized_pnl_today,
        }
        if 'timestamp' in raw_snapshot:
            payload['timestamp'] = raw_snapshot['timestamp']

        return AccountSnapshot.model_validate(payload)

    @staticmethod
    def _blocked_by_risk_result(signal: TradingSignal, reason: str, decision: RiskDecision) -> ExecutionResult:
        return ExecutionResult(
            ok=False,
            status='blocked_by_risk',
            dry_run=True,
            signal=signal,
            message=reason,
            risk_decision=decision,
        )

    def execute(self, request: object) -> ExecutionResult:
        raw_signal, request_dry_run, snapshot = self._as_execution_request(request)
        signal = self._normalize_signal(raw_signal)

        risk_decision: RiskDecision
        try:
            resolved_snapshot = self._resolve_snapshot(snapshot)
            risk_decision = get_guardian_service().approve_execution(
                signal=signal.model_dump(mode='json'),
                snapshot=resolved_snapshot,
            )
        except Exception as exc:
            risk_decision = RiskDecision(
                approved=False,
                reason=f'Risk evaluation failed closed: {exc}',
                risk_level='danger',
                halt_active=True,
                drawdown=None,
            )

        if not risk_decision.approved or risk_decision.halt_active:
            event_bus.emit(
                'trading.execution.blocked_by_risk',
                'ExecutionEngine',
                'Execution blocked by risk guardian',
                {'signal_id': signal.id, 'reason': risk_decision.reason},
            )
            return self._blocked_by_risk_result(signal=signal, reason=risk_decision.reason, decision=risk_decision)

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
                risk_decision=risk_decision,
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
                risk_decision=risk_decision,
            )

        effective_dry_run = request_dry_run or self.settings.dry_run
        if effective_dry_run:
            result = ExecutionResult(
                ok=True,
                status='simulated',
                dry_run=True,
                signal=signal,
                message='Dry-run execution simulated successfully.',
                risk_decision=risk_decision,
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
                risk_decision=risk_decision,
            )

        result = self.mt5_adapter.send_order(signal)
        if result.risk_decision is None:
            result = result.model_copy(update={'risk_decision': risk_decision})
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
