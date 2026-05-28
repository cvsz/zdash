from typing import Dict, Any, Optional
from app.billing.billing_adapters import BillingProviderAdapter
from app.billing.models import Subscription
from app.core.config import settings

class StripeAdapter(BillingProviderAdapter):
    def __init__(self):
        self.enabled = settings.STRIPE_ENABLED
        self.secret_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    def create_customer(self, organization: Any) -> str:
        if not self.enabled:
            return ""
        return f"cus_stripe_{organization.id}"

    def create_checkout_session(self, organization_id: str, plan_id: str) -> str:
        if not self.enabled:
            return ""
        return f"https://checkout.stripe.com/c/pay/{organization_id}"

    def get_subscription(self, provider_subscription_id: str) -> Optional[Subscription]:
        return None

    def cancel_subscription(self, provider_subscription_id: str) -> bool:
        return True

    def create_billing_portal_session(self, organization_id: str) -> str:
        if not self.enabled:
            return ""
        return f"https://billing.stripe.com/p/session/{organization_id}"

    def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        if not self.enabled or not self.webhook_secret:
            return {"ok": False, "error": "Stripe webhook not configured properly"}
        return {"ok": True, "event": "stripe.event"}
