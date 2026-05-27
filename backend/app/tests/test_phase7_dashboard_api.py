from app.api import agents as agents_api
from app.api import logs as logs_api
from app.core.config import get_settings
from app.core.events import event_bus


def _assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {"ok", "data", "error", "timestamp"}


def test_agents_api_includes_all_stable_agents() -> None:
    body = agents_api.list_agents()
    _assert_envelope(body)
    assert body["ok"] is True

    agents = body["data"]["agents"]
    ids = {item["id"] for item in agents}

    assert {
        "ceo",
        "janie",
        "guardian",
        "friday",
        "joe",
        "editor",
        "graphic",
        "social",
        "trading",
    }.issubset(ids)

    trading = next(item for item in agents if item["id"] == "trading")
    assert trading["name"] == "Damien Cross"


def test_logs_api_returns_recent_event_logs() -> None:
    event_bus.emit(
        event_type="system.test.event",
        source="test",
        message="phase07.4 log compatibility check",
        payload={"phase": "07.4"},
    )

    body = logs_api.list_logs(limit=20)
    _assert_envelope(body)
    assert body["ok"] is True

    events = body["data"]["events"]
    assert isinstance(events, list)
    assert events
    assert any(event.get("type") == "system.test.event" for event in events)


def test_cors_default_origins_support_frontend_dev_server() -> None:
    settings = get_settings()
    origins = {origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()}

    assert "http://localhost:5173" in origins
    assert "http://127.0.0.1:5173" in origins
