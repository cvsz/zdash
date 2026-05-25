from app.risk.guardian_service import GuardianService
from app.risk.models import AccountSnapshot


def _snapshot(equity: float = 10000.0) -> AccountSnapshot:
    return AccountSnapshot(
        balance=10000.0,
        equity=equity,
        peak_equity=10000.0,
        daily_start_equity=10000.0,
        open_positions=0,
        floating_pnl=equity - 10000.0,
        realized_pnl_today=equity - 10000.0,
    )


def test_normal_risk_approves() -> None:
    service = GuardianService()
    decision = service.check(_snapshot(10000.0))
    assert decision.approved is True
    assert decision.risk_level == 'normal'


def test_active_halt_blocks() -> None:
    service = GuardianService()
    service.halt('maintenance', source='manual')
    decision = service.approve_execution(signal={'symbol': 'XAUUSD'}, snapshot=_snapshot(10000.0))
    assert decision.approved is False
    assert decision.halt_active is True


def test_emergency_drawdown_blocks() -> None:
    service = GuardianService()
    decision = service.check(_snapshot(5000.0))
    assert decision.approved is False
    assert decision.risk_level == 'emergency'


def test_manual_halt_blocks() -> None:
    service = GuardianService()
    service.halt('manual halt', source='manual')
    decision = service.check(_snapshot(10000.0))
    assert decision.approved is False


def test_resume_allows_again_if_risk_normal() -> None:
    service = GuardianService()
    service.halt('manual halt', source='manual')
    service.resume('safe again')
    decision = service.check(_snapshot(10000.0))
    assert decision.approved is True
