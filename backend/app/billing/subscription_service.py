from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

import app.billing.plan_catalog as catalog
from app.billing.billing_adapters import BillingProviderAdapter
from app.billing.models import (
    BillingPlan,
    PlanTier,
    Subscription,
    SubscriptionStatus,
)
from app.core.config import settings
from app.core.events import event_bus
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# helpers                                                                      #
# --------------------------------------------------------------------------- #


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _get_adapter() -> BillingProviderAdapter:
    """Return the configured billing adapter."""
    if settings.stripe_enabled and settings.billing_provider == "stripe":
        from app.billing.stripe_adapter import StripeAdapter

        return StripeAdapter()
    from app.billing.mock_billing_adapter import MockBillingAdapter

    return MockBillingAdapter()


def _get_or_create_plan(db: Any, plan_tier: str) -> BillingPlan | None:
    plan = db.execute(
        select(BillingPlan).where(BillingPlan.tier == plan_tier)
    ).scalar()
    if plan:
        return plan
    catalog_plan = catalog.get_plan(plan_tier)
    if not catalog_plan:
        return None
    plan = BillingPlan(
        id=plan_tier,
        tier=plan_tier,
        name=catalog_plan.name,
        description=catalog_plan.description,
        price_monthly=float(catalog_plan.price_monthly or 0),
        price_yearly=float(catalog_plan.price_yearly) if catalog_plan.price_yearly else None,
        features=list(catalog_plan.features),
        limits=dict(catalog_plan.limits),
        is_public=catalog_plan.is_public,
    )
    db.add(plan)
    db.flush()
    return plan


# --------------------------------------------------------------------------- #
# public service methods                                                       #
# --------------------------------------------------------------------------- #


def list_plans() -> list[dict[str, Any]]:
    """Return the public plan catalog."""
    plans = []
    for tier in [PlanTier.free, PlanTier.starter, PlanTier.pro, PlanTier.enterprise]:
        p = catalog.get_plan(tier.value)
        if p:
            plans.append(
                {
                    "id": p.tier.value,
                    "tier": p.tier.value,
                    "name": p.name,
                    "description": p.description,
                    "price_monthly": p.price_monthly,
                    "price_yearly": p.price_yearly,
                    "features": p.features,
                    "limits": p.limits,
                }
            )
    event_bus.emit(
        "billing.plan.listed",
        "billing.subscription_service",
        "Plan catalog listed",
        {"count": len(plans)},
    )
    return plans


def get_status(organization_id: str) -> dict[str, Any]:
    """Return current billing status for an organization."""
    with SessionLocal() as db:
        sub = db.execute(
            select(Subscription)
            .where(Subscription.organization_id == organization_id)
            .order_by(Subscription.created_at.desc())
        ).scalar()
        if not sub:
            return {
                "status": "none",
                "plan_tier": "free",
                "plan_id": None,
                "provider": settings.billing_provider,
                "cancel_at_period_end": False,
                "current_period_end": None,
                "trial_ends_at": None,
            }

        plan = db.execute(
            select(BillingPlan).where(BillingPlan.id == sub.plan_id)
        ).scalar()

        return {
            "status": sub.status if isinstance(sub.status, str) else sub.status.value,
            "plan_id": sub.plan_id,
            "plan_tier": plan.tier if plan else "unknown",
            "provider": sub.provider,
            "provider_customer_id": sub.provider_customer_id,
            "cancel_at_period_end": sub.cancel_at_period_end,
            "current_period_start": (
                sub.current_period_start.isoformat()
                if sub.current_period_start
                else None
            ),
            "current_period_end": (
                sub.current_period_end.isoformat()
                if sub.current_period_end
                else None
            ),
            "trial_ends_at": (
                sub.trial_ends_at.isoformat() if sub.trial_ends_at else None
            ),
        }


def start_checkout(organization_id: str, plan_id: str) -> dict[str, Any]:
    """Begin a checkout session for the given plan."""
    if not settings.billing_enabled:
        return {"ok": False, "error": "BILLING_PROVIDER_NOT_CONFIGURED"}

    catalog_plan = catalog.get_plan(plan_id)
    if not catalog_plan:
        return {"ok": False, "error": "PLAN_NOT_FOUND"}

    adapter = _get_adapter()
    try:
        checkout_url = adapter.create_checkout_session(organization_id, plan_id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Checkout session creation failed: %s", exc)
        return {"ok": False, "error": "BILLING_PROVIDER_NOT_CONFIGURED"}

    event_bus.emit(
        "billing.checkout.started",
        "billing.subscription_service",
        f"Checkout started for plan {plan_id}",
        {"organization_id": organization_id, "plan_id": plan_id},
    )
    return {"ok": True, "checkout_url": checkout_url}


def open_billing_portal(organization_id: str) -> dict[str, Any]:
    """Open billing portal for an organization."""
    if not settings.billing_enabled:
        return {"ok": False, "error": "BILLING_PROVIDER_NOT_CONFIGURED"}

    adapter = _get_adapter()
    try:
        portal_url = adapter.create_billing_portal_session(organization_id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Billing portal session failed: %s", exc)
        return {"ok": False, "error": "BILLING_PROVIDER_NOT_CONFIGURED"}

    return {"ok": True, "portal_url": portal_url}


def cancel_subscription(organization_id: str) -> dict[str, Any]:
    """Cancel the active subscription for an organization."""
    with SessionLocal() as db:
        sub = db.execute(
            select(Subscription)
            .where(Subscription.organization_id == organization_id)
            .where(
                Subscription.status.in_(
                    [SubscriptionStatus.active.value, SubscriptionStatus.trialing.value]
                )
            )
        ).scalar()
        if not sub:
            return {"ok": False, "error": "SUBSCRIPTION_INACTIVE"}

        adapter = _get_adapter()
        if sub.provider_subscription_id:
            try:
                adapter.cancel_subscription(sub.provider_subscription_id)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Provider cancel failed, marking locally: %s", exc)

        sub.cancel_at_period_end = True
        sub.updated_at = utc_now()  # type: ignore[attr-defined]
        db.commit()

    event_bus.emit(
        "billing.subscription.canceled",
        "billing.subscription_service",
        f"Subscription canceled for org {organization_id}",
        {"organization_id": organization_id},
    )
    return {"ok": True, "status": "cancel_at_period_end"}


def sync_subscription_from_provider(organization_id: str) -> dict[str, Any]:
    """Sync subscription state from the provider (placeholder)."""
    with SessionLocal() as db:
        sub = db.execute(
            select(Subscription)
            .where(Subscription.organization_id == organization_id)
        ).scalar()
        if not sub or not sub.provider_subscription_id:
            return {"ok": False, "error": "SUBSCRIPTION_INACTIVE"}

        adapter = _get_adapter()
        provider_data = adapter.get_subscription(sub.provider_subscription_id)
        if not provider_data:
            return {"ok": False, "error": "SUBSCRIPTION_INACTIVE"}

        # Map provider status if present
        provider_status = provider_data.get("status")
        if provider_status and hasattr(SubscriptionStatus, provider_status):
            sub.status = provider_status
        sub.updated_at = utc_now()  # type: ignore[attr-defined]
        db.commit()

    event_bus.emit(
        "billing.subscription.updated",
        "billing.subscription_service",
        f"Subscription synced from provider for org {organization_id}",
        {"organization_id": organization_id},
    )
    return {"ok": True}


def apply_mock_plan(organization_id: str, plan_tier: str) -> dict[str, Any]:
    """Apply a plan directly — only allowed in mock/development mode.

    This is guarded by the billing_apply_mock_plan permission at the API layer.
    """
    if (
        settings.billing_provider != "mock"
        and not getattr(settings, "debug", False)
    ):
        return {"ok": False, "error": "Not allowed outside mock or debug mode"}

    valid_tiers = {t.value for t in PlanTier}
    if plan_tier not in valid_tiers:
        return {"ok": False, "error": "PLAN_NOT_FOUND"}

    with SessionLocal() as db:
        plan = _get_or_create_plan(db, plan_tier)
        if not plan:
            return {"ok": False, "error": "PLAN_NOT_FOUND"}

        sub = db.execute(
            select(Subscription).where(
                Subscription.organization_id == organization_id
            )
        ).scalar()
        if sub:
            old_plan = sub.plan_id
            sub.plan_id = plan.id
            sub.status = SubscriptionStatus.active.value
            sub.updated_at = utc_now()  # type: ignore[attr-defined]
        else:
            old_plan = None
            sub = Subscription(
                id=str(uuid.uuid4()),
                organization_id=organization_id,
                plan_id=plan.id,
                status=SubscriptionStatus.active.value,
                provider="mock",
                provider_customer_id=f"cus_mock_{organization_id[:8]}",
                provider_subscription_id=f"sub_mock_{uuid.uuid4().hex[:8]}",
            )
            db.add(sub)
        db.commit()

    event_bus.emit(
        "billing.subscription.updated",
        "billing.subscription_service",
        f"Mock plan applied: {plan_tier} for org {organization_id}",
        {
            "organization_id": organization_id,
            "plan_tier": plan_tier,
            "previous_plan": old_plan,
        },
    )
    return {"ok": True, "plan_tier": plan_tier, "status": "active"}
