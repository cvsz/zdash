from app.marketplace.safety import check_plugin_action

def test_safety_check_plugin_action_allowed():
    ok, msg = check_plugin_action("get_summary", {"data": "test"})
    assert ok is True
    assert msg == "ok"
    
    ok, msg = check_plugin_action("export_data", {})
    assert ok is True

def test_safety_check_plugin_action_blocked():
    ok, msg = check_plugin_action("live_trade_action", {})
    assert ok is False
    assert msg == "PLUGIN_SAFETY_BLOCKED"

    ok, msg = check_plugin_action("REAL_IOT_switch", {})
    assert ok is False
    assert msg == "PLUGIN_SAFETY_BLOCKED"
    
    ok, msg = check_plugin_action("real_social_post", {})
    assert ok is False
    assert msg == "PLUGIN_SAFETY_BLOCKED"
