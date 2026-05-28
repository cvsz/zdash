from datetime import datetime
from typing import Optional, List, Any
from enum import Enum
from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models import Timestamped, _id


class PlanTier(str, Enum):
    free = "free"
    starter = "starter"
    pro = "pro"
    enterprise = "enterprise"


class SubscriptionStatus(str, Enum):
    trialing = "trialing"
    active = "active"
    past_due = "past_due"
    canceled = "canceled"
    expired = "expired"
    suspended = "suspended"


class BillingPlan(Base, Timestamped):
    __tablename__ = "billing_plans"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    tier: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    price_monthly: Mapped[float] = mapped_column(Float, default=0.0)
    price_yearly: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String, default="USD")
    features: Mapped[list] = mapped_column(JSON, default=list)
    limits: Mapped[dict] = mapped_column(JSON, default=dict)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)


class Subscription(Base, Timestamped):
    __tablename__ = "subscriptions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    organization_id: Mapped[str] = mapped_column(String, index=True)
    plan_id: Mapped[str] = mapped_column(String, ForeignKey("billing_plans.id"))
    status: Mapped[str] = mapped_column(String, default=SubscriptionStatus.trialing.value, index=True)
    provider: Mapped[str] = mapped_column(String, default="mock")
    provider_customer_id: Mapped[str] = mapped_column(String, default="")
    provider_subscription_id: Mapped[str] = mapped_column(String, default="")
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


class UsageRecord(Base, Timestamped):
    __tablename__ = "usage_records"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    organization_id: Mapped[str] = mapped_column(String, index=True)
    workspace_id: Mapped[str] = mapped_column(String, index=True, default="")
    metric: Mapped[str] = mapped_column(String, index=True)
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    source: Mapped[str] = mapped_column(String, default="")
    resource_id: Mapped[str] = mapped_column(String, default="")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class Invoice(Base, Timestamped):
    __tablename__ = "invoices"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    organization_id: Mapped[str] = mapped_column(String, index=True)
    provider: Mapped[str] = mapped_column(String, default="mock")
    provider_invoice_id: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="open")
    amount_due: Mapped[float] = mapped_column(Float, default=0.0)
    amount_paid: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String, default="USD")
    hosted_invoice_url: Mapped[str] = mapped_column(String, default="")
    invoice_pdf_url: Mapped[str] = mapped_column(String, default="")
    due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class EntitlementDecision(BaseModel):
    allowed: bool
    feature: str
    reason: str
    plan_tier: str
    required_tier: Optional[str] = None
    quota: Optional[float] = None
    usage: Optional[float] = None
    timestamp: datetime


class UsageSummary(BaseModel):
    organization_id: str
    workspace_id: str
    metric: str
    used: float
    limit: float
    remaining: float
    reset_at: Optional[datetime] = None
    percent_used: float
