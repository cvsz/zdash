from fastapi.testclient import TestClient
from app.main import app
from app.auth.jwt import create_access_token
from app.db.session import SessionLocal
from app.db.models import User
from app.marketplace.plugin_registry import BUILTINS
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

with SessionLocal() as db:
    user = db.query(User).filter(User.email == "test_marketplace@zeaz.dev").first()
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email="test_marketplace@zeaz.dev",
            password_hash="test",
            role="admin",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    token = create_access_token(sub=user.id, role="admin")

with patch("app.billing.entitlement_service.check_feature") as mock_billing_feat, \
     patch("app.api.marketplace.consume") as mock_api_consume, \
     patch("app.marketplace.plugin_service.check_feature") as mock_feat, \
     patch("app.marketplace.plugin_service.consume") as mock_consume, \
     patch("app.marketplace.plugin_service.AuditService.log") as mock_audit:
    
    class MockDecision:
        allowed = True
    mock_billing_feat.return_value = MockDecision()
    mock_api_consume.return_value = MockDecision()
    mock_feat.return_value = MockDecision()
    mock_consume.return_value = MockDecision()
    
    client = TestClient(app)
    res = client.post(
        "/api/marketplace/install",
        json={"plugin_id": BUILTINS[0].id, "workspace_id": "test-ws", "config": {}},
        headers={"Authorization": f"Bearer {token}"}
    )
    print("STATUS:", res.status_code)
    print("JSON:", res.json())
