from app.billing.models import PlanTier, SubscriptionStatus, BillingPlan, Subscription, UsageRecord, UsageSummary, Invoice, EntitlementDecision
from datetime import datetime, timezone

def test_plan_tier_enum():
    assert PlanTier.free.value == "free"
    assert PlanTier.starter.value == "starter"
    assert PlanTier.pro.value == "pro"
    assert PlanTier.enterprise.value == "enterprise"

def test_subscription_status_enum():
    assert SubscriptionStatus.active.value == "active"
    assert SubscriptionStatus.canceled.value == "canceled"
    assert SubscriptionStatus.past_due.value == "past_due"

def test_billing_plan_defaults():
    plan = BillingPlan(price_monthly=0.0, currency="USD", is_public=True, features=[], limits={})
    assert plan.price_monthly == 0.0
    assert plan.currency == "USD"
    assert plan.is_public is True
    assert isinstance(plan.features, list)
    assert isinstance(plan.limits, dict)

def test_subscription_defaults():
    sub = Subscription(status=SubscriptionStatus.trialing.value, provider="mock", cancel_at_period_end=False, metadata_json={})
    assert sub.status == SubscriptionStatus.trialing.value
    assert sub.provider == "mock"
    assert sub.cancel_at_period_end is False
    assert isinstance(sub.metadata_json, dict)

def test_usage_record_defaults():
    rec = UsageRecord(quantity=1.0, metadata_json={})
    assert rec.quantity == 1.0
    assert isinstance(rec.metadata_json, dict)

def test_invoice_defaults():
    inv = Invoice(status="open", amount_due=0.0, currency="USD")
    assert inv.status == "open"
    assert inv.amount_due == 0.0
    assert inv.currency == "USD"

def test_usage_summary_model():
    summary = UsageSummary(
        organization_id="org_1",
        workspace_id="ws_1",
        metric="api_requests",
        used=100.0,
        limit=1000.0,
        remaining=900.0,
        percent_used=10.0
    )
    assert summary.used == 100.0
    assert summary.percent_used == 10.0

def test_entitlement_decision_model():
    decision = EntitlementDecision(
        allowed=True,
        feature="feature.scheduler",
        reason="Quota OK",
        plan_tier="pro",
        timestamp=datetime.now(timezone.utc)
    )
    assert decision.allowed is True
    assert decision.feature == "feature.scheduler"
