from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy import select

from app.billing.models import BillingPlan, EntitlementDecision, Subscription
from app.billing.usage_meter import get_metric_summary
from app.core.config import settings
from app.db.session import SessionLocal
from app.tenancy.dependencies import get_tenant_context
from app.tenancy.tenant_context import TenantContext


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_plan_for_org(organization_id: str) -> BillingPlan:
    with SessionLocal() as db:
        sub = db.execute(
            select(Subscription)
            .where(Subscription.organization_id == organization_id)
            .where(Subscription.status.in_(["active", "trialing"]))
        ).scalar()

        if sub:
            plan = db.execute(
                select(BillingPlan).where(BillingPlan.id == sub.plan_id)
            ).scalar()
            if plan:
                return plan

        free_plan = db.execute(
            select(BillingPlan).where(BillingPlan.tier == "free")
        ).scalar()
        if not free_plan:
            from app.billing.models import PlanTier

            return BillingPlan(
                id="free",
                tier=PlanTier.free.value,
                name="Free",
                features=[],
                limits={},
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
        timestamp=utc_now(),
    )


def check_quota(
    organization_id: str,
    workspace_id: str,
    metric: str,
    increment: float = 1.0,
) -> EntitlementDecision:
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
            timestamp=utc_now(),
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
        timestamp=utc_now(),
    )


def require_feature(feature: str) -> Callable:
    def _dependency(tenant: TenantContext = Depends(get_tenant_context)) -> str:
        if not settings.billing_enabled:
            return feature
        decision = check_feature(
            getattr(tenant, "organization_id", "default"), feature
        )
        if not decision.allowed and settings.billing_fail_closed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=decision.reason,
            )
        return feature

    return _dependency


def require_quota(metric: str, increment: float = 1.0) -> Callable:
    def _dependency(tenant: TenantContext = Depends(get_tenant_context)) -> str:
        if not settings.billing_enabled:
            return metric
        org_id = getattr(tenant, "organization_id", "default")
        ws_id = getattr(tenant, "workspace_id", "default")
        decision = check_quota(org_id, ws_id, metric, increment)
        if not decision.allowed and settings.usage_enforcement_enabled:
            raise HTTPException(status_code=402, detail="QUOTA_EXCEEDED")
        return metric

    return _dependency
