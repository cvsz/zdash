from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.billing.models import Subscription

class BillingProviderAdapter(ABC):
    
    @abstractmethod
    def create_customer(self, organization: Any) -> str:
        pass
        
    @abstractmethod
    def create_checkout_session(self, organization_id: str, plan_id: str) -> str:
        pass
        
    @abstractmethod
    def get_subscription(self, provider_subscription_id: str) -> Optional[Subscription]:
        pass
        
    @abstractmethod
    def cancel_subscription(self, provider_subscription_id: str) -> bool:
        pass
        
    @abstractmethod
    def create_billing_portal_session(self, organization_id: str) -> str:
        pass
        
    @abstractmethod
    def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        pass
