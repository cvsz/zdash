from __future__ import annotations

from typing import Any

from app.realtime.schemas import (
    RealtimeChannel,
    RealtimeEventEnvelope,
    RealtimeSeverity,
    utc_now_iso,
)

CHANNELS: tuple[RealtimeChannel, ...] = ("events", "risk", "scheduler", "content")

_EVENT_ALIASES: dict[str, str] = {
    "risk.warning": "risk.alert",
    "risk.execution.blocked": "risk.alert",
    "risk.execution.approved": "risk.resume",
    "scheduler.job.started": "scheduler.started",
    "scheduler.job.completed": "scheduler.completed",
    "scheduler.job.failed": "scheduler.failed",
    "content.draft.created": "content.created",
    "content.publish.simulated": "content.published",
}


def normalize_event_type(event_type: str, payload: dict[str, Any] | None = None) -> str:
    normalized = _EVENT_ALIASES.get(event_type, event_type)
    if normalized == "risk.check.completed" and payload:
        risk_level = str(payload.get("risk_level", "")).lower()
        if risk_level in {"warning", "danger", "emergency"}:
            return "risk.alert"
    return normalized


def severity_for_event(event_type: str, payload: dict[str, Any] | None = None) -> RealtimeSeverity:
    normalized = normalize_event_type(event_type, payload)
    lowered = normalized.lower()

    if any(keyword in lowered for keyword in ("failed", "danger", "halt", "blocked")):
        return "danger"
    if "warning" in lowered or normalized == "risk.alert":
        return "warning"
    if any(keyword in lowered for keyword in ("connected", "resumed", "resume", "completed", "approved")):
        return "success"
    return "info"


def channels_for_event(event_type: str) -> set[RealtimeChannel]:
    normalized = normalize_event_type(event_type)
    channels: set[RealtimeChannel] = {"events"}
    lowered = normalized.lower()

    if lowered.startswith("risk.") or lowered.startswith("guardian."):
        channels.add("risk")
    if lowered.startswith("scheduler."):
        channels.add("scheduler")
    if lowered.startswith("content.") or lowered.startswith("editor.") or lowered.startswith("social."):
        channels.add("content")

    return channels


def build_event_envelope(
    *,
    event_type: str,
    source: str,
    payload: dict[str, Any] | None = None,
    severity: RealtimeSeverity | None = None,
    timestamp: str | None = None,
) -> RealtimeEventEnvelope:
    safe_payload = dict(payload or {})
    normalized_type = normalize_event_type(event_type, safe_payload)
    return RealtimeEventEnvelope(
        type=normalized_type,
        source=source,
        severity=severity or severity_for_event(normalized_type, safe_payload),
        payload=safe_payload,
        timestamp=timestamp or utc_now_iso(),
    )


def envelope_from_core_event(event: Any) -> RealtimeEventEnvelope:
    payload = dict(getattr(event, "payload", {}) or {})
    message = str(getattr(event, "message", "")).strip()
    if message and "message" not in payload:
        payload["message"] = message

    raw_timestamp = getattr(event, "created_at", None)
    parsed_timestamp = str(raw_timestamp).strip() if raw_timestamp is not None else None

    return build_event_envelope(
        event_type=str(getattr(event, "type", "system.warning")),
        source=str(getattr(event, "source", "system")),
        payload=payload,
        timestamp=parsed_timestamp if parsed_timestamp else None,
    )
