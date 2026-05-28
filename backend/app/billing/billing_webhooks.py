from __future__ import annotations

import logging
from typing import Any

from app.billing.subscription_service import _get_adapter
from app.core.events import event_bus

logger = logging.getLogger(__name__)


def handle_webhook(payload: bytes, signature: str) -> dict[str, Any]:
    """Route an inbound billing provider webhook to the configured adapter.

    Emits ``billing.webhook.received`` on success and
    ``billing.webhook.failed`` on failure.  Never raises — always returns
    a result dict with ``{"ok": bool}``.
    """
    try:
        adapter = _get_adapter()
        result = adapter.handle_webhook(payload, signature)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Billing webhook dispatch error: %s", exc)
        result = {"ok": False, "error": str(exc)}

    event_type = (
        "billing.webhook.received" if result.get("ok") else "billing.webhook.failed"
    )
    event_bus.emit(
        event_type,
        "billing.billing_webhooks",
        f"Webhook {'received' if result.get('ok') else 'failed'}",
        {
            "ok": result.get("ok"),
            "event": result.get("event"),
            "error": result.get("error"),
        },
    )
    return result
