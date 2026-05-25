from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.events import event_bus
from app.risk.models import AccountSnapshot
from app.risk.guardian_service import get_guardian_service
from app.trading.risk_models import ExecutionRequest


class ExecutionEngine:
    def __init__(self) -> None:
        self.settings = get_settings()

    @staticmethod
    def _default_snapshot() -> AccountSnapshot:
        return AccountSnapshot(
            balance=10000.0,
            equity=10000.0,
            peak_equity=10000.0,
            daily_start_equity=10000.0,
            open_positions=0,
            floating_pnl=0.0,
            realized_pnl_today=0.0,
        )

    def execute(self, req: ExecutionRequest) -> dict:
        guardian_service = get_guardian_service()
        snapshot = req.snapshot or self._default_snapshot()
        signal_payload = req.signal.model_dump()

        decision = guardian_service.approve_execution(signal=signal_payload, snapshot=snapshot)

        if not decision.approved or decision.halt_active:
            event_bus.emit(
                'trading.execution.blocked_by_risk',
                'ExecutionEngine',
                'Execution blocked by risk decision',
                {'risk_decision': decision.model_dump(mode='json'), 'signal': signal_payload},
            )
            return {
                'ok': False,
                'status': 'blocked_by_risk',
                'dry_run': self.settings.dry_run,
                'signal': signal_payload,
                'risk_decision': decision.model_dump(mode='json'),
                'message': decision.reason,
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }

        if self.settings.dry_run:
            return {
                'ok': True,
                'status': 'simulated',
                'dry_run': True,
                'signal': signal_payload,
                'risk_decision': decision.model_dump(mode='json'),
                'message': 'Dry-run execution simulated.',
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }

        if not self.settings.live_trading_ack:
            return {
                'ok': False,
                'status': 'blocked_by_config',
                'dry_run': False,
                'signal': signal_payload,
                'risk_decision': decision.model_dump(mode='json'),
                'message': 'LIVE_TRADING_ACK=false blocks non-dry-run execution.',
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }

        if not self.settings.risk_guardian_enabled:
            return {
                'ok': False,
                'status': 'blocked_by_config',
                'dry_run': False,
                'signal': signal_payload,
                'risk_decision': decision.model_dump(mode='json'),
                'message': 'RISK_GUARDIAN_ENABLED=false blocks live execution.',
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }

        return {
            'ok': True,
            'status': 'executed',
            'dry_run': False,
            'signal': signal_payload,
            'risk_decision': decision.model_dump(mode='json'),
            'message': 'Execution approved and marked executed (simulation mode).',
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
