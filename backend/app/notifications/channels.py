from __future__ import annotations

from typing import Any

from app.core.config import get_settings


def sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    blocked_fragments = {"token", "password", "secret", "api_key", "private_key"}
    safe_payload: dict[str, Any] = {}
    for key, value in payload.items():
        normalized = key.lower()
        if any(fragment in normalized for fragment in blocked_fragments):
            continue
        safe_payload[key] = value
    return safe_payload


def dispatch_dry_run(channel_name: str, title: str, message: str, payload: dict[str, Any]) -> dict:
    return {
        "channel": channel_name,
        "status": "dry_run",
        "title": title,
        "message": message,
        "payload": sanitize_payload(payload),
    }


def dispatch_email(
    channel_name: str,
    title: str,
    message: str,
    payload: dict[str, Any],
) -> dict:
    settings = get_settings()
    if (
        not settings.email_notifications_enabled
        or not settings.smtp_host.strip()
        or not settings.smtp_username.strip()
        or not settings.smtp_password.strip()
        or not settings.smtp_from.strip()
    ):
        return {
            "channel": channel_name,
            "status": "blocked",
            "reason": "email channel not configured",
            "payload": sanitize_payload(payload),
        }
    return {
        "channel": channel_name,
        "status": "stubbed",
        "title": title,
        "message": message,
        "payload": sanitize_payload(payload),
    }


def dispatch_webhook(
    channel_name: str,
    title: str,
    message: str,
    payload: dict[str, Any],
) -> dict:
    settings = get_settings()
    if not settings.webhook_notifications_enabled or not settings.webhook_url.strip():
        return {
            "channel": channel_name,
            "status": "blocked",
            "reason": "webhook channel disabled",
            "payload": sanitize_payload(payload),
        }
    return {
        "channel": channel_name,
        "status": "stubbed",
        "title": title,
        "message": message,
        "payload": sanitize_payload(payload),
    }
