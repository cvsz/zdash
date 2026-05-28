from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum

class LicenseStatus(str, Enum):
    active = "active"
    expired = "expired"
    revoked = "revoked"

class ExportStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

from app.db.base import Base
from app.db.models import Timestamped, _id


class EnterpriseLicense(Base, Timestamped):
    __tablename__ = "enterprise_licenses"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    organization_id: Mapped[str] = mapped_column(String, index=True)
    license_key_hash: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="active", index=True)
    tier: Mapped[str] = mapped_column(String, default="enterprise")
    seats: Mapped[int] = mapped_column(Integer, default=-1)
    features_json: Mapped[list] = mapped_column("features", JSON, default=list)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    offline_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    issued_to: Mapped[str] = mapped_column(String, default="")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


class BrandingSettings(Base, Timestamped):
    __tablename__ = "branding_settings"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    organization_id: Mapped[str] = mapped_column(String, index=True)
    workspace_id: Mapped[str] = mapped_column(String, index=True, default="")
    brand_name: Mapped[str] = mapped_column(String, default="zDash")
    logo_url: Mapped[str] = mapped_column(String, default="")
    primary_color: Mapped[str] = mapped_column(String, default="#7c3aed")
    accent_color: Mapped[str] = mapped_column(String, default="#22c55e")
    support_email: Mapped[str] = mapped_column(String, default="")
    custom_domain: Mapped[str] = mapped_column(String, default="")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


class ExportBundle(Base, Timestamped):
    __tablename__ = "export_bundles"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    organization_id: Mapped[str] = mapped_column(String, index=True)
    workspace_id: Mapped[str] = mapped_column(String, index=True, default="")
    export_type: Mapped[str] = mapped_column(String, default="full")
    status: Mapped[str] = mapped_column(String, default="pending", index=True)
    file_path: Mapped[str] = mapped_column(String, default="")
    include_audit_logs: Mapped[bool] = mapped_column(Boolean, default=True)
    include_content: Mapped[bool] = mapped_column(Boolean, default=True)
    include_backtests: Mapped[bool] = mapped_column(Boolean, default=True)
    include_scheduler: Mapped[bool] = mapped_column(Boolean, default=True)
    include_secrets: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str] = mapped_column(String, default="")
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class OnboardingChecklist(Base, Timestamped):
    __tablename__ = "onboarding_checklists"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    organization_id: Mapped[str] = mapped_column(String, index=True)
    workspace_id: Mapped[str] = mapped_column(String, index=True, default="")
    completed_steps_json: Mapped[list] = mapped_column("completed_steps", JSON, default=list)
    pending_steps_json: Mapped[list] = mapped_column("pending_steps", JSON, default=list)
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)
