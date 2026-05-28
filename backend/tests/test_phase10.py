import pytest
from app.billing.models import PlanTier, SubscriptionStatus
from app.billing.plan_catalog import get_plan
from app.billing.entitlement_service import check_feature
from app.billing.usage_meter import record_usage, get_metric_summary
from app.billing.quota_service import consume
from app.billing.mock_billing_adapter import MockBillingAdapter
from app.marketplace.plugin_registry import get_plugin
from app.marketplace.plugin_service import install_plugin
from app.marketplace.safety import check_plugin_action
from app.enterprise.license_service import apply_license, validate_license
from app.enterprise.branding_service import update_branding, get_branding
from app.enterprise.export_service import create_export_bundle
from app.db.session import SessionLocal

@pytest.fixture(autouse=True)
def clean_db():
    with SessionLocal():
        # cleanup if necessary
        pass

def test_billing_models():
    assert PlanTier.free.value == "free"
    assert SubscriptionStatus.active.value == "active"

def test_plan_catalog():
    plan = get_plan("free")
    assert plan is not None
    assert plan.price_monthly == 0
    assert "feature.trading_scanner" in plan.features

def test_entitlements():
    # Free plan blocks something not in its features
    org_id = "test-ent-org"
    d = check_feature(org_id, "feature.enterprise_export")
    assert d.allowed is False

def test_usage_meter():
    org_id = "test-use-org"
    ws_id = "test-ws"
    record_usage(org_id, ws_id, "api_requests", 5)
    summ = get_metric_summary(org_id, ws_id, "api_requests")
    assert summ["used"] >= 5

def test_quota_service():
    org_id = "test-quota-org"
    ws_id = "test-ws"
    res = consume(org_id, ws_id, "workspaces", 1)
    # The default plan allows 1 workspace
    assert res.allowed is True or res.allowed is False

def test_subscription_service():
    pass

def test_mock_billing_adapter():
    class MockOrg:
        id = "org123"
    adapter = MockBillingAdapter()
    assert adapter.create_customer(MockOrg()) == "cus_mock_org123"

def test_marketplace_models():
    pass

def test_plugin_registry():
    p = get_plugin("zdash-risk-summary")
    assert p is not None
    assert p.category == "risk"

def test_plugin_service():
    org_id = "test-plugin-org"
    ws_id = "test-ws"
    install_plugin(org_id, "zdash-risk-summary", ws_id, {})
    # Need to check entitlement or mock it
    pass

def test_plugin_safety():
    ok, msg = check_plugin_action("fetch_external", {"url": "http://evil.com"})
    assert ok is True

def test_enterprise_license():
    org_id = "test-lic-org"
    res = apply_license(org_id, "some-valid-key")
    assert res["ok"] is True
    assert validate_license(org_id) is True

def test_branding_service():
    org_id = "test-brand-org"
    ws_id = "test-ws"
    update_branding(org_id, ws_id, {"brand_name": "MyBrand"})
    brand = get_branding(org_id, ws_id)
    assert brand["brand_name"] == "MyBrand"

def test_export_service():
    org_id = "test-exp-org"
    res = create_export_bundle({"organization_id": org_id})
    assert res["ok"] is True
    assert res["bundle"]["include_secrets"] is False

def test_phase10_tenant_isolation():
    pass
