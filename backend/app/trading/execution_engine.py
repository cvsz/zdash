from app.core.config import get_settings
from app.core.database import session_scope
from app.core.events import event_bus
from app.repositories import Repository
from app.risk.halt_flag import get_halt_state
from app.trading.risk_models import ExecutionRequest


class ExecutionEngine:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _live_mode_approved(self) -> bool:
        with session_scope() as session:
            approval = Repository(session).latest_live_mode_approval()
        return bool(approval and approval.approved and self.settings.admin_approved_live_mode)

    def execute(self, req: ExecutionRequest) -> dict:
        halt = get_halt_state()
        if halt.halted:
            event_bus.emit('execution_blocked', 'ExecutionEngine', {'reason': halt.reason})
            return {'executed': False, 'reason': f'HALT_ACTIVE: {halt.reason}', 'mode': 'blocked'}

        live_allowed = (
            (not self.settings.dry_run)
            and self.settings.live_trading_ack
            and self.settings.risk_guardian_enabled
            and self._live_mode_approved()
        )

        if not live_allowed:
            event_bus.emit('execution_dry_run', 'ExecutionEngine', {'signal': req.signal.model_dump()})
            return {
                'executed': False,
                'mode': 'dry_run',
                'reason': 'Live trading safety gates not satisfied.',
                'signal': req.signal.model_dump(),
            }

        event_bus.emit('execution_live', 'ExecutionEngine', {'signal': req.signal.model_dump()})
        return {'executed': True, 'mode': 'live', 'ticket_id': 'SIMULATED-LIVE-TICKET'}
