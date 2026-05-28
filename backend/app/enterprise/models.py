from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON
from datetime import datetime, timezone
from app.db.base import Base
from app.db.models import _id

class EnterpriseLicense(Base):
    __tablename__ = "enterprise_licenses"

    id = Column(String, primary_key=True, default=_id)
    organization_id = Column(String, unique=True, nullable=False, index=True)
    license_key_hash = Column(String, nullable=False)
    status = Column(String, nullable=False)  # active, expired, revoked
    tier = Column(String, nullable=False)
    seats = Column(Integer, nullable=False, default=10)
    features = Column(JSON, default=list)
    expires_at = Column(DateTime)
    offline_mode = Column(Boolean, default=False)
    issued_to = Column(String)
    metadata_json = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class BrandingSettings(Base):
    __tablename__ = "branding_settings"

    id = Column(String, primary_key=True, default=_id)
    organization_id = Column(String, nullable=False, index=True)
    workspace_id = Column(String, nullable=True, index=True)
    brand_name = Column(String, nullable=False, default="zDash")
    logo_url = Column(String)
    primary_color = Column(String, default="#7c3aed")
    accent_color = Column(String, default="#22c55e")
    support_email = Column(String)
    custom_domain = Column(String)
    metadata_json = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ExportBundle(Base):
    __tablename__ = "export_bundles"

    id = Column(String, primary_key=True, default=_id)
    organization_id = Column(String, nullable=False, index=True)
    workspace_id = Column(String, nullable=True, index=True)
    export_type = Column(String, nullable=False)  # full, partial
    status = Column(String, nullable=False)  # pending, completed, failed
    file_path = Column(String)
    include_audit_logs = Column(Boolean, default=True)
    include_content = Column(Boolean, default=True)
    include_backtests = Column(Boolean, default=True)
    include_scheduler = Column(Boolean, default=True)
    include_secrets = Column(Boolean, default=False)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime)


class OnboardingChecklist(Base):
    __tablename__ = "onboarding_checklists"

    id = Column(String, primary_key=True, default=lambda: f"chk-{datetime.now(timezone.utc).timestamp()}")
    organization_id = Column(String, nullable=False, index=True)
    workspace_id = Column(String, index=True)
    completed_steps = Column(JSON, default=list)
    pending_steps = Column(JSON, default=list)
    progress_percent = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

