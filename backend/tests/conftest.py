import pytest

from app.backtesting.backtest_service import reset_backtest_service
from app.core.config import get_settings
from app.core.events import event_bus
from app.risk.guardian_service import reset_guardian_service
from app.scheduler.friday_agent import reset_friday_agent
from app.scheduler.scheduler_service import reset_scheduler_service


from app.db.migrations import run_migrations

run_migrations()

@pytest.fixture(autouse=True)
def reset_risk_runtime_state() -> None:
    get_settings.cache_clear()
    reset_backtest_service()
    reset_guardian_service()
    reset_friday_agent()
    reset_scheduler_service()
    event_bus.clear()
    yield
    event_bus.clear()
    reset_backtest_service()
    reset_friday_agent()
    reset_scheduler_service()
    reset_guardian_service()
    get_settings.cache_clear()
