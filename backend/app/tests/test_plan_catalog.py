from app.billing.plan_catalog import PLANS, list_public_plans, get_plan

def test_plan_catalog_has_all_tiers():
    assert "free" in PLANS
    assert "starter" in PLANS
    assert "pro" in PLANS
    assert "enterprise" in PLANS

def test_free_plan_limits():
    plan = get_plan("free")
    assert plan is not None
    assert plan.limits["workspaces"] == 1
    assert plan.limits["users"] == 1
    assert plan.limits["agents"] == "basic"
    assert plan.price_monthly == 0
    assert "feature.realtime_stream" in plan.features

def test_starter_plan_limits():
    plan = get_plan("starter")
    assert plan is not None
    assert plan.limits["workspaces"] == 2
    assert plan.limits["support"] == "email"

def test_enterprise_plan_custom_quotas():
    plan = get_plan("enterprise")
    assert plan is not None
    assert plan.limits["custom_quotas"] is True
    assert plan.limits["sso_ready"] is True
    assert plan.limits["audit_export"] is True

def test_list_public_plans():
    plans = list_public_plans()
    # Assuming all 4 default plans are public by default
    assert len(plans) == 4
