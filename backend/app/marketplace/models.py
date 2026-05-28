"""Marketplace models — Phase 10.4

ORM tables: PluginManifest, PluginInstallation
Pydantic schemas: PluginActionResult
Enums: PluginStatus, PluginInstallStatus
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models import Timestamped, _id


# ------------------------------------------------------------------ #
# Enums                                                                #
# ------------------------------------------------------------------ #


class PluginStatus(str, Enum):
    draft = "draft"
    review = "review"
    approved = "approved"
    rejected = "rejected"
    deprecated = "deprecated"
    disabled = "disabled"


class PluginInstallStatus(str, Enum):
    installed = "installed"
    enabled = "enabled"
    disabled = "disabled"
    failed = "failed"
    removed = "removed"


# ------------------------------------------------------------------ #
# ORM models                                                           #
# ------------------------------------------------------------------ #


class PluginManifest(Base, Timestamped):
    """Metadata record for a single plugin version."""

    __tablename__ = "plugin_manifests"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    name: Mapped[str] = mapped_column(String, index=True, default="")
    slug: Mapped[str] = mapped_column(String, unique=True, index=True, default="")
    version: Mapped[str] = mapped_column(String, default="1.0.0")
    description: Mapped[str] = mapped_column(Text, default="")
    author: Mapped[str] = mapped_column(String, default="zDash")
    category: Mapped[str] = mapped_column(String, index=True, default="general")
    status: Mapped[str] = mapped_column(
        String, default=PluginStatus.approved.value, index=True
    )
    required_features: Mapped[list] = mapped_column(JSON, default=list)
    required_permissions: Mapped[list] = mapped_column(JSON, default=list)
    config_schema: Mapped[dict] = mapped_column(JSON, default=dict)
    default_config: Mapped[dict] = mapped_column(JSON, default=dict)
    entrypoint: Mapped[str] = mapped_column(String, default="")
    safety_level: Mapped[str] = mapped_column(String, default="sandbox")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


class PluginInstallation(Base, Timestamped):
    """Tenant-scoped installation record."""

    __tablename__ = "plugin_installations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    organization_id: Mapped[str] = mapped_column(String, index=True)
    workspace_id: Mapped[str] = mapped_column(String, index=True, default="")
    plugin_id: Mapped[str] = mapped_column(
        String, ForeignKey("plugin_manifests.id"), index=True
    )
    version: Mapped[str] = mapped_column(String, default="1.0.0")
    status: Mapped[str] = mapped_column(
        String, default=PluginInstallStatus.installed.value, index=True
    )
    config_json: Mapped[dict] = mapped_column("config", JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    installed_by: Mapped[str] = mapped_column(String, default="system")
    installed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )


# ------------------------------------------------------------------ #
# Pydantic response schemas                                            #
# ------------------------------------------------------------------ #


class PluginActionResult(BaseModel):
    plugin_id: str
    action: str
    ok: bool
    message: str
    output: dict[str, Any] = {}
    dry_run: bool = True
    timestamp: datetime

    model_config = {"from_attributes": True}


def manifest_to_dict(m: PluginManifest) -> dict[str, Any]:
    """Safe serialisation of a PluginManifest ORM row."""
    return {
        "id": m.id,
        "name": m.name,
        "slug": m.slug,
        "version": m.version,
        "description": m.description,
        "author": m.author,
        "category": m.category,
        "status": m.status,
        "required_features": m.required_features or [],
        "required_permissions": m.required_permissions or [],
        "config_schema": m.config_schema or {},
        "default_config": m.default_config or {},
        "entrypoint": m.entrypoint,
        "safety_level": m.safety_level,
        "metadata": m.metadata_json or {},
    }


def installation_to_dict(inst: PluginInstallation) -> dict[str, Any]:
    """Safe serialisation of a PluginInstallation ORM row."""
    return {
        "id": inst.id,
        "organization_id": inst.organization_id,
        "workspace_id": inst.workspace_id,
        "plugin_id": inst.plugin_id,
        "version": inst.version,
        "status": inst.status,
        "config": inst.config_json or {},
        "enabled": inst.enabled,
        "installed_by": inst.installed_by,
        "installed_at": (
            inst.installed_at.isoformat() if isinstance(inst.installed_at, datetime) else None
        ),
    }
