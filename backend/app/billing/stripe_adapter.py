from app.core.config import get_settings
class StripeBillingAdapter:
    def __init__(self): self.s=get_settings()
    def _ensure(self):
        if not (self.s.stripe_enabled and self.s.stripe_secret_key and self.s.stripe_webhook_secret): raise RuntimeError('BILLING_PROVIDER_NOT_CONFIGURED')
    def create_customer(self, organization): self._ensure(); return {'id':'stripe_customer_placeholder'}
    def create_checkout_session(self,organization_id,plan_id): self._ensure(); return {'id':'stripe_checkout_placeholder','url':'https://checkout.stripe.com/pay/mock'}
    def get_subscription(self,provider_subscription_id): self._ensure(); return {'id':provider_subscription_id,'status':'active'}
    def cancel_subscription(self,provider_subscription_id): self._ensure(); return {'id':provider_subscription_id,'status':'canceled'}
    def create_billing_portal_session(self,organization_id): self._ensure(); return {'url':'https://billing.stripe.com/p/session/mock'}
    def handle_webhook(self,payload,signature):
        if not self.s.stripe_webhook_secret: return {'ok':False,'error':'missing webhook secret'}
        return {'ok':True,'event':'placeholder'}
