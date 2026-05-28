from .models import BillingPlan, PlanTier

FEATURES = [
    "feature.trading_scanner",
    "feature.risk_guardian",
    "feature.scheduler",
    "feature.backtesting",
    "feature.optimization",
    "feature.content_pipeline",
    "feature.iot",
    "feature.marketplace",
    "feature.white_label",
    "feature.audit_export",
    "feature.enterprise_export",
    "feature.realtime_stream",
]
PLANS = {
    "free": BillingPlan(
        id="free",
        tier=PlanTier.free,
        name="Free",
        description="Safe starter",
        price_monthly=0,
        price_yearly=0,
        features=FEATURES[:7] + ["feature.realtime_stream"],
        limits={
            "workspaces": 1,
            "users": 1,
            "agents": "basic",
            "backtests_per_month": 25,
            "optimizations_per_month": 5,
            "content_items_per_month": 25,
            "scheduler_jobs": 3,
            "marketplace_plugins": 0,
            "realtime_events": "limited",
            "support": "community",
        },
        is_public=True,
    ),
    "starter": BillingPlan(
        id="starter",
        tier=PlanTier.starter,
        name="Starter",
        description="Growth",
        price_monthly=29,
        price_yearly=290,
        features=FEATURES[:10] + ["feature.realtime_stream"],
        limits={
            "workspaces": 2,
            "users": 3,
            "backtests_per_month": 250,
            "optimizations_per_month": 25,
            "content_items_per_month": 250,
            "scheduler_jobs": 10,
            "marketplace_plugins": 3,
            "support": "email",
        },
        is_public=True,
    ),
    "pro": BillingPlan(
        id="pro",
        tier=PlanTier.pro,
        name="Pro",
        description="Scale",
        price_monthly=99,
        price_yearly=990,
        features=FEATURES,
        limits={
            "workspaces": 10,
            "users": 15,
            "backtests_per_month": 2500,
            "optimizations_per_month": 250,
            "content_items_per_month": 2500,
            "scheduler_jobs": 100,
            "marketplace_plugins": 25,
            "support": "priority",
        },
        is_public=True,
    ),
    "enterprise": BillingPlan(
        id="enterprise",
        tier=PlanTier.enterprise,
        name="Enterprise",
        description="Custom",
        price_monthly=0,
        price_yearly=None,
        features=FEATURES,
        limits={
            "workspaces": "unlimited", 
            "users": "unlimited",
            "custom_quotas": True,
            "sso_ready": True,
            "audit_export": True,
            "white_label": True,
            "offline_license": True,
            "support": "dedicated",
        },
        is_public=True,
    ),
}


def list_public_plans():
    return [p for p in PLANS.values() if p.is_public]


def get_plan(plan_id: str):
    return PLANS.get(plan_id)
