from __future__ import annotations

from typing import Any

from app.realtime.schemas import RealtimeCategory, RealtimeChannel, RealtimeEventEnvelope, RealtimeSeverity, utc_now_iso

CHANNELS: tuple[RealtimeChannel, ...] = ("events", "risk", "scheduler", "content")
_EVENT_ALIASES = {
    "risk.warning": "risk.alert",
    "risk.execution.blocked": "risk.alert",
    "scheduler.job.started": "scheduler.started",
    "scheduler.job.completed": "scheduler.completed",
    "content.draft.created": "content.created",
}


def normalize_event_type(event_type: str, payload: dict[str, Any] | None = None) -> str:
    return _EVENT_ALIASES.get(event_type, event_type)


def _category_for_event(event_type: str) -> RealtimeCategory:
    prefix = normalize_event_type(event_type).split(".", 1)[0].lower()
    if prefix in {"system", "trading", "risk", "scheduler", "content", "iot", "admin", "audit"}:
        return prefix  # type: ignore[return-value]
    return "system"


def severity_for_event(event_type: str, payload: dict[str, Any] | None = None) -> RealtimeSeverity:
    lowered = normalize_event_type(event_type).lower()
    if "critical" in lowered or "halt" in lowered or "blocked" in lowered:
        return "critical"
    if "warning" in lowered or lowered.startswith("risk."):
        return "warning"
    return "info"


def channels_for_event(event_type: str) -> set[RealtimeChannel]:
    category = _category_for_event(event_type)
    channels: set[RealtimeChannel] = {"events"}
    if category == "risk": channels.add("risk")
    if category == "scheduler": channels.add("scheduler")
    if category == "content": channels.add("content")
    return channels


def build_event_envelope(*, event_type: str, source: str, payload: dict[str, Any] | None = None, severity: RealtimeSeverity | None = None, message: str | None = None, timestamp: str | None = None) -> RealtimeEventEnvelope:
    safe_payload = dict(payload or {})
    normalized = normalize_event_type(event_type, safe_payload)
    return RealtimeEventEnvelope(
        timestamp=timestamp or utc_now_iso(),
        category=_category_for_event(normalized),
        type=normalized,
        severity=severity or severity_for_event(normalized, safe_payload),
        source=source,
        message=message or str(safe_payload.get("message", "")).strip(),
        data=safe_payload,
        payload=safe_payload,
    )


def envelope_from_core_event(event: Any) -> RealtimeEventEnvelope:
    payload = dict(getattr(event, "payload", {}) or {})
    message = str(getattr(event, "message", "")).strip()
    if message and "message" not in payload:
        payload["message"] = message
    return build_event_envelope(
        event_type=str(getattr(event, "type", "system.event")),
        source=str(getattr(event, "source", "system")),
        payload=payload,
        message=message,
    )
