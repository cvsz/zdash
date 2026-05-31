from __future__ import annotations

from app.api.realtime import router


ALLOWED_CHANNELS = {"events", "risk", "scheduler", "content"}


def test_allowed_channels_set_contains_expected() -> None:
    assert ALLOWED_CHANNELS == {"events", "risk", "scheduler", "content"}


def test_channel_validation_rejects_unknown() -> None:
    invalid = {"", "admin", "chat", "alerts", "system", "events/extra", "EVENTS"}
    for ch in invalid:
        assert ch not in ALLOWED_CHANNELS, f"{ch!r} should not be allowed"


def test_channel_validation_accepts_known() -> None:
    for ch in ALLOWED_CHANNELS:
        assert ch in ALLOWED_CHANNELS


def test_events_compat_endpoint_registered() -> None:
    ws_paths = {r.path for r in router.routes}
    assert "/api/realtime/ws/events" in ws_paths
    assert "/api/realtime/ws/{channel}" in ws_paths
    assert "/api/realtime/ws" in ws_paths
