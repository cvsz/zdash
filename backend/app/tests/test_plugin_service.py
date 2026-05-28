import pytest
from app.marketplace.plugin_service import (
    install_plugin,
    enable_plugin,
    disable_plugin,
    uninstall_plugin,
    run_plugin_action,
    list_installations
)
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

def test_plugin_lifecycle():
    org_id = "test-org-plugins"
    ws_id = "test-ws"
    plugin_id = BUILTINS[0].id
    
    # 1. Install
    res = install_plugin(org_id, plugin_id, ws_id, {"setting": "test"}, "user-1")
    assert res.get("ok") is True
    inst_id = res["id"]
    
    insts = list_installations(org_id, ws_id)
    assert len(insts) > 0
    assert insts[0].id == inst_id
    
    # 2. Enable
    res = enable_plugin(org_id, inst_id, "user-1")
    assert res.get("ok") is True
    
    # 3. Run Action
    res = run_plugin_action(org_id, inst_id, "summarize", {"data": 123}, "user-1")
    assert res.get("ok") is True
    assert res["action"] == "summarize"
    
    # 4. Run blocked Action
    res = run_plugin_action(org_id, inst_id, "live_trade", {}, "user-1")
    assert res.get("ok") is False
    assert res.get("error") == "PLUGIN_SAFETY_BLOCKED"
    
    # 5. Disable
    res = disable_plugin(org_id, inst_id, "user-1")
    assert res.get("ok") is True
    
    # Run action when disabled
    res = run_plugin_action(org_id, inst_id, "summarize", {}, "user-1")
    assert res.get("ok") is False
    assert res.get("error") == "PLUGIN_DISABLED"
    
    # 6. Uninstall
    res = uninstall_plugin(org_id, inst_id, "user-1")
    assert res.get("ok") is True
    
    insts = list_installations(org_id, ws_id)
    assert not any(i.id == inst_id for i in insts)
