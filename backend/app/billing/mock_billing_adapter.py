import hashlib


class MockBillingAdapter:
    def _id(self, prefix: str, key: str) -> str:
        return f"{prefix}_{hashlib.sha1(key.encode()).hexdigest()[:12]}"

    def create_customer(self, organization):
        return {"id": self._id("cus", str(organization))}

    def create_checkout_session(self, organization_id, plan_id):
        return {
            "id": self._id("cs", f"{organization_id}:{plan_id}"),
            "url": f"https://mock-billing.local/checkout/{organization_id}/{plan_id}",
        }

    def get_subscription(self, provider_subscription_id):
        return {"id": provider_subscription_id, "status": "active"}

    def cancel_subscription(self, provider_subscription_id):
        return {"id": provider_subscription_id, "status": "canceled"}

    def create_billing_portal_session(self, organization_id):
        return {"url": f"https://mock-billing.local/portal/{organization_id}"}

    def handle_webhook(self, payload, signature):
        return {"ok": True, "payload": payload, "signature": bool(signature)}
