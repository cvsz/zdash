from __future__ import annotations

import hashlib
import hmac
import time
from typing import Literal

from pydantic import BaseModel

MAX_TIMESTAMP_DRIFT_SECONDS = 300


class WebhookValidationResult(BaseModel):
    valid: bool
    reason: Literal[
        "accepted",
        "timestamp_expired",
        "invalid_signature",
        "missing_credentials",
    ]


class TradingViewWebhookValidator:
    """Validates TradingView webhook payloads via HMAC-SHA256 with replay prevention.

    Fail closed: any missing credential, expired timestamp, or signature mismatch
    rejects the payload.
    """

    def __init__(self, secret: str | None = None) -> None:
        self._secret = secret.encode("utf-8") if secret else None

    def validate_payload(
        self,
        signature: str | None,
        timestamp: int | None,
        payload: str,
        now: float | None = None,
    ) -> WebhookValidationResult:
        if not self._secret or not signature or timestamp is None:
            return WebhookValidationResult(valid=False, reason="missing_credentials")

        current = now if now is not None else time.time()
        if abs(current - timestamp) > MAX_TIMESTAMP_DRIFT_SECONDS:
            return WebhookValidationResult(valid=False, reason="timestamp_expired")

        expected = hmac.new(
            self._secret,
            f"{timestamp}.{payload}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return WebhookValidationResult(valid=False, reason="invalid_signature")

        return WebhookValidationResult(valid=True, reason="accepted")
