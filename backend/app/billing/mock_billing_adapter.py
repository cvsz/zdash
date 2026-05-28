from __future__ import annotations

import hashlib
from typing import Any

from app.billing.billing_adapters import BillingProviderAdapter


class MockBillingAdapter(BillingProviderAdapter):
    """Deterministic mock billing adapter — no external API calls.

    Safe for tests and development.  All IDs are derived from inputs
    so they are stable across calls.
    """

    _CHECKOUT_BASE = "https://mock-billing.test/checkout"
    _PORTAL_BASE = "https://mock-billing.test/portal"

    # ------------------------------------------------------------------ #
    # helpers                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _stable_id(prefix: str, seed: str) -> str:
        """Return a deterministic short ID from a seed string."""
        digest = hashlib.sha256(seed.encode()).hexdigest()[:12]
        return f"{prefix}_{digest}"

    # ------------------------------------------------------------------ #
    # BillingProviderAdapter implementation                                #
    # ------------------------------------------------------------------ #

    def create_customer(self, organization: Any) -> str:
        org_id = getattr(organization, "id", str(organization))
        return self._stable_id("cus_mock", org_id)

    def create_checkout_session(self, organization_id: str, plan_id: str) -> str:
        token = self._stable_id("sess", f"{organization_id}:{plan_id}")
        return f"{self._CHECKOUT_BASE}/{token}"

    def get_subscription(
        self, provider_subscription_id: str
    ) -> dict[str, Any] | None:
        # Mock adapter has no live state — return None (no subscription found)
        return None

    def cancel_subscription(self, provider_subscription_id: str) -> bool:
        return True

    def create_billing_portal_session(self, organization_id: str) -> str:
        token = self._stable_id("portal", organization_id)
        return f"{self._PORTAL_BASE}/{token}"

    def handle_webhook(
        self, payload: bytes, signature: str
    ) -> dict[str, Any]:
        return {"ok": True, "event": "mock.noop", "provider": "mock"}
