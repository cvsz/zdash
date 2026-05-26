import pytest

from app.core.config import get_settings
from app.core.events import event_bus
from app.risk.guardian_service import reset_guardian_service


@pytest.fixture(autouse=True)
def reset_risk_runtime_state() -> None:
    get_settings.cache_clear()
    reset_guardian_service()
    event_bus.clear()
    yield
    event_bus.clear()
    reset_guardian_service()
    get_settings.cache_clear()
