from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_user
from app.auth.models import AuthSession
from app.core.config import get_settings
from app.main import app
from app.risk.guardian_service import reset_guardian_service
from app.trading.models import ExecutionRequest, TradingSignal


def _payload() -> dict:
    signal = TradingSignal(
        symbol="XAUUSD",
        timeframe="M5",
        direction="buy",
        strategy="ob_aggressive",
        confidence=0.71,
        entry=2300.0,
        stop_loss=2298.0,
        take_profit=2304.0,
        reason="legacy route RBAC regression",
    )
    return ExecutionRequest(
        signal=signal,
        dry_run=True,
        confirmation=False,
    ).model_dump(mode="json")


def _post_legacy_as(role: str):
    app.dependency_overrides[get_current_user] = lambda: AuthSession(
        username="rbac-test-user",
        role=role,
    )
    try:
        return TestClient(app).post("/api/trading/dry-run", json=_payload())
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
        reset_guardian_service()


def test_legacy_dry_run_rejects_viewer_without_execution_permission() -> None:
    response = _post_legacy_as("viewer")

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "HTTP_403"


def test_legacy_dry_run_allows_operator_and_remains_simulated() -> None:
    response = _post_legacy_as("operator")

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["data"]["status"] == "simulated"
    assert response.json()["data"]["dry_run"] is True
