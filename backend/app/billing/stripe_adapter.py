from __future__ import annotations

import logging
from typing import Any

from app.billing.billing_adapters import BillingProviderAdapter

logger = logging.getLogger(__name__)


class StripeAdapter(BillingProviderAdapter):
    """Stripe-compatible billing adapter shell.

    Real Stripe mode requires:
    - STRIPE_ENABLED=true
    - STRIPE_SECRET_KEY set
    - STRIPE_WEBHOOK_SECRET set for webhook verification

    The adapter fails safely when the ``stripe`` SDK is not installed or
    when credentials are missing.  Raw card data is never stored or logged.
    The secret key is never emitted to logs.
    """

    def __init__(self) -> None:
        from app.core.config import settings

        self._enabled: bool = settings.stripe_enabled
        # Store only a flag indicating whether secret is present — never log the value.
        self._has_secret_key: bool = bool(settings.stripe_secret_key)
        self._has_webhook_secret: bool = bool(settings.stripe_webhook_secret)
        # Keep references for use in methods (not logged).
        self._secret_key: str = settings.stripe_secret_key
        self._webhook_secret: str = settings.stripe_webhook_secret
        self._price_map: dict[str, str] = {
            "starter": settings.stripe_price_starter,
            "pro": settings.stripe_price_pro,
            "enterprise": settings.stripe_price_enterprise,
        }

    # ------------------------------------------------------------------ #
    # internal                                                             #
    # ------------------------------------------------------------------ #

    def _stripe_client(self) -> Any:
        """Return the stripe module, or raise ImportError with a helpful message."""
        try:
            import stripe  # type: ignore[import-untyped]

            if self._has_secret_key:
                stripe.api_key = self._secret_key  # noqa: SIM910
            return stripe
        except ImportError as exc:
            raise ImportError(
                "stripe SDK not installed. Add 'stripe' to backend/requirements.txt."
            ) from exc

    def _require_enabled(self) -> None:
        if not self._enabled:
            raise RuntimeError(
                "BILLING_PROVIDER_NOT_CONFIGURED: "
                "Stripe is disabled. Set STRIPE_ENABLED=true."
            )
        if not self._has_secret_key:
            raise RuntimeError(
                "BILLING_PROVIDER_NOT_CONFIGURED: "
                "STRIPE_SECRET_KEY is not set."
            )

    # ------------------------------------------------------------------ #
    # BillingProviderAdapter implementation                                #
    # ------------------------------------------------------------------ #

    def create_customer(self, organization: Any) -> str:
        if not self._enabled:
            return ""
        self._require_enabled()
        stripe = self._stripe_client()
        org_id = getattr(organization, "id", str(organization))
        org_name = getattr(organization, "name", org_id)
        customer = stripe.Customer.create(
            metadata={"organization_id": org_id},
            name=org_name,
        )
        return customer["id"]

    def create_checkout_session(self, organization_id: str, plan_id: str) -> str:
        if not self._enabled:
            return ""
        self._require_enabled()
        stripe = self._stripe_client()
        price_id = self._price_map.get(plan_id, "")
        if not price_id:
            raise ValueError(f"PLAN_NOT_FOUND: No Stripe price for plan '{plan_id}'")
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            metadata={"organization_id": organization_id},
            success_url="https://app/billing/success",
            cancel_url="https://app/billing/cancel",
        )
        return session["url"]

    def get_subscription(
        self, provider_subscription_id: str
    ) -> dict[str, Any] | None:
        if not self._enabled:
            return None
        self._require_enabled()
        stripe = self._stripe_client()
        try:
            sub = stripe.Subscription.retrieve(provider_subscription_id)
            return dict(sub)
        except Exception:  # noqa: BLE001
            return None

    def cancel_subscription(self, provider_subscription_id: str) -> bool:
        if not self._enabled:
            return False
        self._require_enabled()
        stripe = self._stripe_client()
        try:
            stripe.Subscription.modify(
                provider_subscription_id, cancel_at_period_end=True
            )
            return True
        except Exception:  # noqa: BLE001
            return False

    def create_billing_portal_session(self, organization_id: str) -> str:
        if not self._enabled:
            return ""
        self._require_enabled()
        stripe = self._stripe_client()
        session = stripe.billing_portal.Session.create(
            customer=organization_id,
            return_url="https://app/billing",
        )
        return session["url"]

    def handle_webhook(
        self, payload: bytes, signature: str
    ) -> dict[str, Any]:
        if not self._enabled:
            return {"ok": False, "error": "BILLING_PROVIDER_NOT_CONFIGURED"}
        if not self._has_webhook_secret:
            logger.warning(
                "Stripe webhook received but STRIPE_WEBHOOK_SECRET is not set. "
                "Signature verification skipped — event rejected for safety."
            )
            return {"ok": False, "error": "BILLING_PROVIDER_NOT_CONFIGURED"}

        stripe = self._stripe_client()
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self._webhook_secret
            )
            return {"ok": True, "event": event["type"], "id": event["id"]}
        except Exception as exc:  # noqa: BLE001
            logger.warning("Stripe webhook signature verification failed: %s", exc)
            return {"ok": False, "error": "WEBHOOK_SIGNATURE_INVALID"}
