from datetime import datetime
from typing import Optional, List, Any
from enum import Enum
from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models import Timestamped, _id


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


class PluginManifest(Base, Timestamped):
    __tablename__ = "plugin_manifests"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    name: Mapped[str] = mapped_column(String, index=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    version: Mapped[str] = mapped_column(String, default="1.0.0")
    description: Mapped[str] = mapped_column(Text, default="")
    author: Mapped[str] = mapped_column(String, default="")
    category: Mapped[str] = mapped_column(String, index=True, default="general")
    status: Mapped[str] = mapped_column(String, default=PluginStatus.draft.value, index=True)
    required_features_json: Mapped[list] = mapped_column("required_features", JSON, default=list)
    required_permissions_json: Mapped[list] = mapped_column("required_permissions", JSON, default=list)
    config_schema_json: Mapped[dict] = mapped_column("config_schema", JSON, default=dict)
    default_config_json: Mapped[dict] = mapped_column("default_config", JSON, default=dict)
    entrypoint: Mapped[str] = mapped_column(String, default="")
    safety_level: Mapped[str] = mapped_column(String, default="sandbox")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


class PluginInstallation(Base, Timestamped):
    __tablename__ = "plugin_installations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_id)
    organization_id: Mapped[str] = mapped_column(String, index=True)
    workspace_id: Mapped[str] = mapped_column(String, index=True)
    plugin_id: Mapped[str] = mapped_column(String, ForeignKey("plugin_manifests.id"))
    version: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default=PluginInstallStatus.installed.value, index=True)
    config_json: Mapped[dict] = mapped_column("config", JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    installed_by: Mapped[str] = mapped_column(String, default="")
    installed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class PluginActionResult(BaseModel):
    plugin_id: str
    action: str
    ok: bool
    message: str
    output: Any
    dry_run: bool
    timestamp: datetime = func.now()
