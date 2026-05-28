from typing import Dict, Any, Optional
from app.billing.billing_adapters import BillingProviderAdapter
from app.billing.models import Subscription

class MockBillingAdapter(BillingProviderAdapter):
    def create_customer(self, organization: Any) -> str:
        return f"cus_mock_{organization.id}"

    def create_checkout_session(self, organization_id: str, plan_id: str) -> str:
        return f"https://mock-billing.test/checkout/{organization_id}/{plan_id}"

    def get_subscription(self, provider_subscription_id: str) -> Optional[Subscription]:
        return None

    def cancel_subscription(self, provider_subscription_id: str) -> bool:
        return True

    def create_billing_portal_session(self, organization_id: str) -> str:
        return f"https://mock-billing.test/portal/{organization_id}"

    def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        return {"ok": True, "event": "mock.event"}
