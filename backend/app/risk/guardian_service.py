from __future__ import annotations

from app.agents.guardian import GuardianAgent
from app.core.config import get_settings
from app.risk.drawdown_guard import DrawdownGuard
from app.risk.halt_flag import HaltFlagStore
from app.risk.kill_switch import KillSwitch
from app.risk.models import AccountSnapshot, DrawdownResult, HaltState, RiskDecision


class GuardianService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.drawdown_guard = DrawdownGuard()
        self.halt_store = HaltFlagStore()
        self.kill_switch = KillSwitch()
        self.guardian = GuardianAgent(
            drawdown_guard=self.drawdown_guard,
            halt_store=self.halt_store,
            kill_switch=self.kill_switch,
        )
        self.latest_decision: RiskDecision | None = None

    def get_status(self) -> dict:
        return {
            'guardian_enabled': self.settings.risk_guardian_enabled,
            'halt_state': self.halt_store.get_state().model_dump(mode='json'),
            'thresholds': {
                'max_daily_drawdown_percent': self.settings.max_daily_drawdown_percent,
                'max_total_drawdown_percent': self.settings.max_total_drawdown_percent,
                'emergency_kill_switch_drawdown_percent': self.settings.emergency_kill_switch_drawdown_percent,
                'soft_halt_drawdown_level_1': self.settings.soft_halt_drawdown_level_1,
                'soft_halt_drawdown_level_2': self.settings.soft_halt_drawdown_level_2,
                'soft_halt_drawdown_level_3': self.settings.soft_halt_drawdown_level_3,
            },
            'current_risk_status': self.latest_decision.risk_level if self.latest_decision else 'unknown',
            'latest_risk_decision': self.latest_decision.model_dump(mode='json') if self.latest_decision else None,
        }

    def check(self, snapshot: AccountSnapshot) -> RiskDecision:
        decision = self.guardian.evaluate_risk(snapshot)
        self.latest_decision = decision
        return decision

    def halt(self, reason: str, source: str = 'manual') -> HaltState:
        return self.halt_store.halt(reason=reason, source=source)

    def resume(self, reason: str, approved: bool = False) -> HaltState:
        if not approved:
            raise ValueError('Explicit approval is required to resume risk halt.')
        if not self.settings.allow_manual_resume:
            raise ValueError('Manual resume is disabled by configuration.')
        return self.halt_store.resume(reason=reason)

    def approve_execution(self, signal: dict, snapshot: AccountSnapshot) -> RiskDecision:
        decision = self.guardian.approve_execution(signal=signal, snapshot=snapshot)
        self.latest_decision = decision
        return decision

    def latest_drawdown(self) -> DrawdownResult | None:
        if not self.latest_decision:
            return None
        return self.latest_decision.drawdown

    def reset(self) -> None:
        self.halt_store.clear()
        self.latest_decision = None


_guardian_service: GuardianService | None = None


def get_guardian_service() -> GuardianService:
    global _guardian_service
    if _guardian_service is None:
        _guardian_service = GuardianService()
    return _guardian_service


def reset_guardian_service() -> None:
    global _guardian_service
    _guardian_service = None


def get_guardian_agent() -> GuardianAgent:
    return get_guardian_service().guardian
