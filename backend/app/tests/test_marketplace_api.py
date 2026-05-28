import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.jwt import create_access_token
from app.db.session import SessionLocal
from app.db.models import User
from app.marketplace.plugin_registry import BUILTINS
import uuid
from datetime import datetime, timezone

@pytest.fixture(scope="module")
def admin_token():
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
        return create_access_token(sub=user.id, role="admin")

@pytest.fixture(scope="module")
def client():
    from unittest.mock import patch
    with patch("app.billing.entitlement_service.check_feature") as mock_billing_feat, \
         patch("app.api.marketplace.consume") as mock_api_consume, \
         patch("app.marketplace.plugin_service.check_feature") as mock_feat, \
         patch("app.marketplace.plugin_service.consume") as mock_consume, \
         patch("app.marketplace.plugin_service.AuditService.log"):
        class MockDecision:
            allowed = True
        mock_billing_feat.return_value = MockDecision()
        mock_api_consume.return_value = MockDecision()
        mock_feat.return_value = MockDecision()
        mock_consume.return_value = MockDecision()
        yield TestClient(app)

def test_list_plugins_api(client, admin_token):
    res = client.get("/api/marketplace/plugins", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert res.json()["ok"] is True
    assert len(res.json()["data"]["plugins"]) == len(BUILTINS)

def test_get_plugin_api(client, admin_token):
    res = client.get(f"/api/marketplace/plugins/{BUILTINS[0].id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert res.json()["ok"] is True
    assert res.json()["data"]["plugin"]["id"] == BUILTINS[0].id

def test_install_and_lifecycle_api(client, admin_token):
    # Install
    res = client.post(
        "/api/marketplace/install",
        json={"plugin_id": BUILTINS[0].id, "workspace_id": "test-ws", "config": {}},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert res.json()["ok"] is True
    inst_id = res.json()["data"]["id"]
    
    # Enable
    res = client.post(
        f"/api/marketplace/installations/{inst_id}/enable",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert res.json()["ok"] is True
    
    # Run
    res = client.post(
        f"/api/marketplace/installations/{inst_id}/run",
        json={"action": "test_action", "payload": {}},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert res.json()["ok"] is True
    
    # Disable
    res = client.post(
        f"/api/marketplace/installations/{inst_id}/disable",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert res.json()["ok"] is True
    
    # Uninstall
    res = client.delete(
        f"/api/marketplace/installations/{inst_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert res.json()["ok"] is True
