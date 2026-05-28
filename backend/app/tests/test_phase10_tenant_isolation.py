import pytest
from app.marketplace.plugin_service import install_plugin, list_installations
from app.marketplace.builtins import BUILTINS

from unittest.mock import patch

@pytest.fixture(autouse=True)
def setup_teardown():
    from app.marketplace.models import PluginInstallation
    from app.db.session import SessionLocal
    with SessionLocal() as db:
        db.query(PluginInstallation).delete()
        db.commit()
        
    with patch("app.marketplace.plugin_service.check_feature") as mock_feat, \
         patch("app.marketplace.plugin_service.consume") as mock_consume, \
         patch("app.marketplace.plugin_service.AuditService.log"):
        class MockDecision:
            allowed = True
        mock_feat.return_value = MockDecision()
        mock_consume.return_value = MockDecision()
        yield

def test_tenant_isolation():
    org1 = "org-1"
    org2 = "org-2"
    ws1 = "ws-1"
    ws2 = "ws-2"
    
    plugin_id = BUILTINS[0].id
    
    # Install for org 1, ws 1
    res1 = install_plugin(org1, plugin_id, ws1, {}, "user-1")
    assert res1.get("ok") is True
    
    # Install for org 2, ws 2
    res2 = install_plugin(org2, plugin_id, ws2, {}, "user-2")
    assert res2.get("ok") is True
    
    # List for org 1
    insts_org1 = list_installations(org1)
    assert len(insts_org1) > 0
    assert all(i.organization_id == org1 for i in insts_org1)
    assert any(i.id == res1["id"] for i in insts_org1)
    assert not any(i.id == res2["id"] for i in insts_org1)
    
    # List for org 2
    insts_org2 = list_installations(org2)
    assert len(insts_org2) > 0
    assert all(i.organization_id == org2 for i in insts_org2)
    assert any(i.id == res2["id"] for i in insts_org2)
    assert not any(i.id == res1["id"] for i in insts_org2)
