from typing import Optional, Any, Callable
from sqlalchemy import select
from app.db.session import SessionLocal
from app.billing.models import EntitlementDecision, Subscription, BillingPlan
from app.billing.usage_meter import get_metric_summary
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def get_plan_for_org(organization_id: str) -> BillingPlan:
    with SessionLocal() as db:
        # First, try to find an active subscription
        sub = db.execute(
            select(Subscription)
            .where(Subscription.organization_id == organization_id)
            .where(Subscription.status.in_(["active", "trialing"]))
        ).scalar()
        
        if sub:
            plan = db.execute(select(BillingPlan).where(BillingPlan.id == sub.plan_id)).scalar()
            if plan:
                return plan
        
        # Fallback to free plan if no active subscription
        free_plan = db.execute(select(BillingPlan).where(BillingPlan.tier == "free")).scalar()
        if not free_plan:
            # If free plan doesn't exist in DB yet, create an emergency mock plan
            from app.billing.models import PlanTier
            return BillingPlan(
                id="free",
                tier=PlanTier.free.value,
                name="Free",
                features=[],
                limits={}
            )
        return free_plan

def check_feature(organization_id: str, feature: str) -> EntitlementDecision:
    plan = get_plan_for_org(organization_id)
    features = plan.features if hasattr(plan, "features") else []
    
    allowed = feature in features
    return EntitlementDecision(
        allowed=allowed,
        feature=feature,
        reason="ok" if allowed else "FEATURE_NOT_ENTITLED",
        plan_tier=plan.tier,
        timestamp=utc_now()
    )

def check_quota(organization_id: str, workspace_id: str, metric: str, increment: float = 1.0) -> EntitlementDecision:
    plan = get_plan_for_org(organization_id)
    limits = plan.limits if hasattr(plan, "limits") else {}
    
    limit = limits.get(metric)
    
    if limit is None or limit == "unlimited" or limit == -1:
        return EntitlementDecision(
            allowed=True,
            feature=metric,
            reason="ok",
            plan_tier=plan.tier,
            quota=None,
            usage=None,
            timestamp=utc_now()
        )
    
    summary = get_metric_summary(organization_id, workspace_id, metric)
    used = summary.get("used", 0.0)
    
    allowed = (used + increment) <= float(limit)
    
    return EntitlementDecision(
        allowed=allowed,
        feature=metric,
        reason="ok" if allowed else "QUOTA_EXCEEDED",
        plan_tier=plan.tier,
        quota=float(limit),
        usage=used,
        timestamp=utc_now()
    )

def require_feature(feature: str) -> Callable[[], str]:
    def _dep() -> str:
        return feature
    return _dep

def require_quota(metric: str, increment: float = 1.0) -> Callable[[], str]:
    def _dep() -> str:
        return metric
    return _dep
