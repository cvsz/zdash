from app.realtime.models import RealtimeEvent


def test_realtime_event_model_defaults() -> None:
    event = RealtimeEvent(type="risk.drawdown.warning", source="risk", payload={"message": "warn"})
    assert event.event_id
    assert event.severity == "info"
    assert event.payload["message"] == "warn"
