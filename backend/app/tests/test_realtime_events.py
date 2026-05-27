from app.core.events import Event
from app.realtime.events import (
    channels_for_event,
    envelope_from_core_event,
    normalize_event_type,
    severity_for_event,
)


def test_normalize_event_type_maps_phase75_aliases() -> None:
    assert normalize_event_type("risk.warning") == "risk.alert"
    assert normalize_event_type("scheduler.job.completed") == "scheduler.completed"
    assert normalize_event_type("content.draft.created") == "content.created"


def test_channels_for_event_routes_by_domain() -> None:
    assert channels_for_event("risk.alert") == {"events", "risk"}
    assert channels_for_event("scheduler.started") == {"events", "scheduler"}
    assert channels_for_event("content.approved") == {"events", "content"}


def test_envelope_from_core_event_preserves_payload_and_message() -> None:
    core_event = Event(
        type="risk.execution.blocked",
        source="guardian",
        message="Execution blocked by policy",
        payload={"halt_active": True},
    )

    envelope = envelope_from_core_event(core_event)

    assert envelope.type == "risk.alert"
    assert envelope.source == "guardian"
    assert envelope.payload["halt_active"] is True
    assert envelope.payload["message"] == "Execution blocked by policy"
    assert severity_for_event(envelope.type, envelope.payload) == "warning"
