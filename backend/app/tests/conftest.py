import pytest
from collections.abc import Generator

from app.agents.registry import reset_registry
from app.backtesting.backtest_service import reset_backtest_service
from app.content.pipeline import reset_content_pipeline
from app.core.config import get_settings
from app.core.events import event_bus
from app.risk.guardian_service import reset_guardian_service
from app.realtime import (
    reset_realtime_broadcaster,
    reset_realtime_connection_manager,
)
from app.scheduler.friday_agent import reset_friday_agent
from app.scheduler.scheduler_service import reset_scheduler_service


@pytest.fixture(autouse=True)
def reset_runtime_state() -> Generator[None, None, None]:
    get_settings.cache_clear()
    reset_backtest_service()
    reset_guardian_service()
    reset_friday_agent()
    reset_scheduler_service()
    reset_content_pipeline()
    reset_realtime_broadcaster()
    reset_realtime_connection_manager()
    reset_registry()
    event_bus.clear()
    yield
    event_bus.clear()
    reset_backtest_service()
    reset_content_pipeline()
    reset_registry()
    reset_friday_agent()
    reset_scheduler_service()
    reset_guardian_service()
    reset_realtime_broadcaster()
    reset_realtime_connection_manager()
    get_settings.cache_clear()
