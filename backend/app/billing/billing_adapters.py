from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BillingProviderAdapter(ABC):
    """Abstract interface for billing provider adapters."""

    @abstractmethod
    def create_customer(self, organization: Any) -> str:
        """Create a customer record in the billing provider.

        Returns provider customer ID.
        """
        ...

    @abstractmethod
    def create_checkout_session(self, organization_id: str, plan_id: str) -> str:
        """Create a checkout session.

        Returns the checkout URL.
        """
        ...

    @abstractmethod
    def get_subscription(
        self, provider_subscription_id: str
    ) -> dict[str, Any] | None:
        """Fetch current subscription data from provider."""
        ...

    @abstractmethod
    def cancel_subscription(self, provider_subscription_id: str) -> bool:
        """Cancel a subscription at the provider.

        Returns True if successful.
        """
        ...

    @abstractmethod
    def create_billing_portal_session(self, organization_id: str) -> str:
        """Create a billing portal session.

        Returns portal URL.
        """
        ...

    @abstractmethod
    def handle_webhook(
        self, payload: bytes, signature: str
    ) -> dict[str, Any]:
        """Handle an incoming webhook from the provider.

        Returns a result dict with at minimum ``{"ok": bool}``.
        """
        ...
