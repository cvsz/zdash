from typing import Dict, Any, List, Optional
from sqlalchemy import select
from app.db.session import SessionLocal
from app.billing.models import Subscription, SubscriptionStatus, PlanTier, BillingPlan
from app.billing.mock_billing_adapter import MockBillingAdapter
from app.billing.stripe_adapter import StripeAdapter
from app.core.config import settings
from datetime import datetime, timezone
import uuid
import app.billing.plan_catalog as catalog

def get_adapter():
    if settings.BILLING_PROVIDER == "stripe":
        return StripeAdapter()
    return MockBillingAdapter()

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def list_plans() -> List[Dict[str, Any]]:
    # In a real app we'd sync this with Stripe/DB. For now, load from static catalog
    plans = []
    for tier in [PlanTier.free, PlanTier.starter, PlanTier.pro, PlanTier.enterprise]:
        p = catalog.get_plan(tier.value)
        if p:
            plans.append({
                "id": p.tier.value,
                "tier": p.tier.value,
                "name": p.name,
                "features": p.features,
                "limits": p.limits
            })
    return plans

def get_status(organization_id: str) -> Dict[str, Any]:
    with SessionLocal() as db:
        sub = db.execute(select(Subscription).where(Subscription.organization_id == organization_id).order_by(Subscription.created_at.desc())).scalar()
        if not sub:
            return {"status": "none", "plan_tier": "free"}
        
        plan = db.execute(select(BillingPlan).where(BillingPlan.id == sub.plan_id)).scalar()
        
        return {
            "status": sub.status.value,
            "plan_id": sub.plan_id,
            "plan_tier": plan.tier if plan else "unknown",
            "cancel_at_period_end": sub.cancel_at_period_end,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None
        }

def start_checkout(organization_id: str, plan_id: str) -> Dict[str, Any]:
    adapter = get_adapter()
    url = adapter.create_checkout_session(organization_id, plan_id)
    return {"ok": True, "checkout_url": url}

def open_billing_portal(organization_id: str) -> Dict[str, Any]:
    adapter = get_adapter()
    url = adapter.create_billing_portal_session(organization_id)
    return {"ok": True, "portal_url": url}

def cancel_subscription(organization_id: str) -> Dict[str, Any]:
    with SessionLocal() as db:
        sub = db.execute(select(Subscription).where(Subscription.organization_id == organization_id).where(Subscription.status.in_(["active", "trialing"]))).scalar()
        if not sub:
            return {"ok": False, "error": "No active subscription"}
        
        adapter = get_adapter()
        if sub.provider_subscription_id:
            adapter.cancel_subscription(sub.provider_subscription_id)
            
        sub.cancel_at_period_end = True
        sub.updated_at = utc_now()
        db.commit()
    
    return {"ok": True, "status": "canceled"}

def sync_subscription_from_provider(organization_id: str) -> Optional[Subscription]:
    # Placeholder for webhook synchronization logic
    pass

def apply_mock_plan(organization_id: str, plan_tier: str) -> Dict[str, Any]:
    # Only allowed in dev/mock
    if settings.BILLING_PROVIDER != "mock" and not settings.DEBUG:
        return {"ok": False, "error": "Not allowed outside mock mode"}
        
    with SessionLocal() as db:
        plan = db.execute(select(BillingPlan).where(BillingPlan.tier == plan_tier)).scalar()
        if not plan:
            # create plan dynamically
            p = catalog.get_plan(plan_tier)
            if not p:
                return {"ok": False, "error": "PLAN_NOT_FOUND"}
            plan = BillingPlan(
                id=plan_tier,
                tier=plan_tier,
                name=p.name,
                features=p.features,
                limits=p.limits
            )
            db.add(plan)
            db.commit()
            
        sub = db.execute(select(Subscription).where(Subscription.organization_id == organization_id)).scalar()
        if sub:
            sub.plan_id = plan.id
            sub.status = SubscriptionStatus.active
            sub.updated_at = utc_now()
        else:
            sub = Subscription(
                organization_id=organization_id,
                plan_id=plan.id,
                status=SubscriptionStatus.active,
                provider="mock",
                provider_customer_id=f"cus_mock_{organization_id}",
                provider_subscription_id=f"sub_mock_{uuid.uuid4().hex[:8]}"
            )
            db.add(sub)
        db.commit()
        
    return {"ok": True, "plan_tier": plan_tier}
