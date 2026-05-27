from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field


def now() -> datetime:
    return datetime.now(timezone.utc)


class DataRegion(str, Enum):
    local = "local"
    us = "us"
    eu = "eu"
    apac = "apac"
    custom = "custom"


class ResidencyEnforcementMode(str, Enum):
    advisory = "advisory"
    enforced = "enforced"
    fail_closed = "fail_closed"


class SovereignProfileStatus(str, Enum):
    draft = "draft"
    active = "active"
    disabled = "disabled"
    archived = "archived"


class KMSProvider(str, Enum):
    mock = "mock"
    aws_kms = "aws_kms"
    gcp_kms = "gcp_kms"
    azure_key_vault = "azure_key_vault"
    hashicorp_vault = "hashicorp_vault"
    custom = "custom"


class RegionRecord(BaseModel):
    id: str
    code: DataRegion
    name: str
    jurisdiction: str = ""
    status: str = "active"
    allowed: bool = True
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)


class DataResidencyRule(BaseModel):
    id: str
    organization_id: str
    workspace_id: str = ""
    allowed_regions: list[DataRegion] = Field(default_factory=list)
    disallowed_regions: list[DataRegion] = Field(default_factory=list)
    default_region: DataRegion = DataRegion.local
    enforcement_mode: ResidencyEnforcementMode = ResidencyEnforcementMode.fail_closed
    applies_to: list[str] = Field(default_factory=lambda: ["all"])
    reason: str = ""
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)


class ResidencyDecision(BaseModel):
    allowed: bool
    source_region: DataRegion
    target_region: DataRegion
    resource_type: str
    reason: str
    enforcement_mode: ResidencyEnforcementMode
    matched_rules: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=now)


class SovereignDeploymentProfile(BaseModel):
    id: str
    organization_id: str
    workspace_id: str = ""
    name: str
    profile_type: str = "standard"
    status: SovereignProfileStatus = SovereignProfileStatus.draft
    data_region: DataRegion = DataRegion.local
    allowed_integrations: list[str] = Field(default_factory=list)
    disabled_features: list[str] = Field(default_factory=list)
    kms_required: bool = False
    offline_supported: bool = True
    policy_bundle_id: str | None = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)


class KMSKeyRecord(BaseModel):
    id: str
    organization_id: str
    workspace_id: str = ""
    provider: KMSProvider = KMSProvider.mock
    key_ref_hash: str
    status: str = "active"
    customer_managed: bool = True
    rotation_required: bool = False
    last_rotated_at: datetime | None = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)


class PolicyBundle(BaseModel):
    id: str
    organization_id: str
    workspace_id: str = ""
    name: str
    version: str = "1.0.0"
    includes_governance: bool = True
    includes_compliance: bool = True
    includes_residency: bool = True
    includes_rbac: bool = True
    includes_safety_gates: bool = True
    file_path: str = ""
    checksum: str = ""
    secrets_excluded: bool = True
    created_by: str = "system"
    created_at: datetime = Field(default_factory=now)
