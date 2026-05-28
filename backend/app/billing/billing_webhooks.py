from typing import Dict, Any
from app.billing.subscription_service import get_adapter

def handle_webhook(payload: bytes, signature: str) -> Dict[str, Any]:
    adapter = get_adapter()
    return adapter.handle_webhook(payload, signature)
