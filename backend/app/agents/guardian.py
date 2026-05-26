from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.core.config import get_settings
from app.risk.drawdown_guard import DrawdownGuard
from app.risk.halt_flag import HaltFlagStore
from app.risk.kill_switch import KillSwitch
from app.risk.models import AccountSnapshot, HaltState, RiskDecision


class GuardianAgent(BaseAgent):
    def __init__(self, drawdown_guard: DrawdownGuard, halt_store: HaltFlagStore, kill_switch: KillSwitch) -> None:
        super().__init__(
            agent_id='guardian',
            name='Victor Hale',
            role='risk_manager',
            metadata={'tier': 'epic', 'legacy_name': 'Guardian'},
        )
        self.drawdown_guard = drawdown_guard
        self.halt_store = halt_store
        self.kill_switch = kill_switch
        self.settings = get_settings()

    def receive_message(self, message):
        snapshot = AccountSnapshot.model_validate(message.context)
        decision = self.evaluate_risk(snapshot)
        return decision.model_dump(mode='json')

    def run_task(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        if task == 'health':
            return self.health_check()
        if not context:
            raise ValueError('Victor Hale task requires account snapshot context.')
        snapshot = AccountSnapshot.model_validate(context)
        return self.evaluate_risk(snapshot).model_dump(mode='json')

    def evaluate_risk(self, snapshot: AccountSnapshot) -> RiskDecision:
        self.status = 'running'
        self.emit_event('risk.check.requested', 'Risk check requested', snapshot.model_dump(mode='json'))

        halt_state = self.halt_store.get_state()

        if not self.settings.risk_guardian_enabled:
            if self.settings.dry_run:
                decision = RiskDecision(
                    approved=True,
                    reason='Guardian disabled; dry-run allowed with warning.',
                    risk_level='warning',
                    halt_active=halt_state.halted,
                    drawdown=self.drawdown_guard.evaluate(snapshot),
                )
                self.emit_event('risk.warning', 'Victor Hale disabled in dry-run mode', {'approved': True})
            else:
                decision = RiskDecision(
                    approved=False,
                    reason='Guardian disabled; live execution blocked.',
                    risk_level='danger',
                    halt_active=halt_state.halted,
                    drawdown=self.drawdown_guard.evaluate(snapshot),
                )
                self.emit_event('risk.execution.blocked', 'Victor Hale disabled for live mode', {'approved': False})
            self.status = 'idle'
            self.emit_event('risk.check.completed', 'Risk check completed', decision.model_dump(mode='json'))
            return decision

        if halt_state.halted:
            decision = RiskDecision(
                approved=False,
                reason=f'Execution blocked: halt active ({halt_state.reason}).',
                risk_level='danger',
                halt_active=True,
                drawdown=self.drawdown_guard.evaluate(snapshot),
            )
            self.status = 'idle'
            self.emit_event('risk.execution.blocked', 'Execution blocked due to active halt', decision.model_dump(mode='json'))
            self.emit_event('risk.check.completed', 'Risk check completed', decision.model_dump(mode='json'))
            return decision

        drawdown = self.drawdown_guard.evaluate(snapshot)

        if self.kill_switch.should_trigger(drawdown):
            state = self.kill_switch.trigger(drawdown=drawdown, halt_store=self.halt_store)
            decision = RiskDecision(
                approved=False,
                reason='Emergency stop triggered.',
                risk_level='emergency',
                halt_active=state.halted,
                drawdown=drawdown,
            )
            self.status = 'idle'
            self.emit_event('risk.execution.blocked', 'Execution blocked by emergency stop', decision.model_dump(mode='json'))
            self.emit_event('risk.check.completed', 'Risk check completed', decision.model_dump(mode='json'))
            return decision

        if drawdown.breached:
            state = self.halt_store.halt(reason=drawdown.breach_reason or 'Drawdown breach', source='guardian')
            decision = RiskDecision(
                approved=False,
                reason=drawdown.breach_reason or 'Drawdown threshold breached.',
                risk_level='danger',
                halt_active=state.halted,
                drawdown=drawdown,
            )
            self.status = 'idle'
            self.emit_event('risk.execution.blocked', 'Execution blocked by drawdown breach', decision.model_dump(mode='json'))
            self.emit_event('risk.check.completed', 'Risk check completed', decision.model_dump(mode='json'))
            return decision

        if drawdown.risk_level == 'warning':
            approved = self.settings.dry_run
            reason = 'Warning risk level: dry-run allowed.' if approved else 'Warning risk level: live execution blocked.'
            decision = RiskDecision(
                approved=approved,
                reason=reason,
                risk_level='warning',
                halt_active=False,
                drawdown=drawdown,
            )
            self.status = 'idle'
            self.emit_event('risk.warning', 'Warning-level drawdown detected', decision.model_dump(mode='json'))
            if approved:
                self.emit_event('risk.execution.approved', 'Execution approved with warning', decision.model_dump(mode='json'))
            else:
                self.emit_event('risk.execution.blocked', 'Execution blocked at warning level', decision.model_dump(mode='json'))
            self.emit_event('risk.check.completed', 'Risk check completed', decision.model_dump(mode='json'))
            return decision

        decision = RiskDecision(
            approved=True,
            reason='Risk level normal. Execution approved.',
            risk_level='normal',
            halt_active=False,
            drawdown=drawdown,
        )
        self.status = 'idle'
        self.emit_event('risk.execution.approved', 'Execution approved', decision.model_dump(mode='json'))
        self.emit_event('risk.check.completed', 'Risk check completed', decision.model_dump(mode='json'))
        return decision

    def approve_execution(self, signal: dict, snapshot: AccountSnapshot) -> RiskDecision:
        self.emit_event('risk.check.requested', 'Execution approval requested', {'signal': signal})
        return self.evaluate_risk(snapshot)

    def manual_halt(self, reason: str) -> HaltState:
        return self.halt_store.halt(reason=reason, source='manual')

    def manual_resume(self, reason: str) -> HaltState:
        settings = get_settings()
        if not settings.allow_manual_resume:
            raise ValueError('Manual resume is disabled by configuration.')
        return self.halt_store.resume(reason=reason)

    def health_check(self) -> dict[str, Any]:
        base = super().health_check()
        base['guardian_enabled'] = self.settings.risk_guardian_enabled
        base['halt_state'] = self.halt_store.get_state().model_dump(mode='json')
        return base
