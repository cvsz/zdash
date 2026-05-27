from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, field_validator


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TwinEntityType(str, Enum):
    organization = "organization"
    workspace = "workspace"
    customer = "customer"
    partner = "partner"
    reseller = "reseller"
    marketplace_listing = "marketplace_listing"
    product_module = "product_module"
    region = "region"
    edge_runner = "edge_runner"
    initiative = "initiative"
    objective = "objective"
    risk = "risk"
    incident = "incident"
    integration = "integration"
    revenue_stream = "revenue_stream"
    support_case = "support_case"


class TwinRelationshipType(str, Enum):
    owns = "owns"
    depends_on = "depends_on"
    influences = "influences"
    blocks = "blocks"
    supports = "supports"
    competes_with = "competes_with"
    supplies = "supplies"
    consumes = "consumes"
    operates_in = "operates_in"
    governed_by = "governed_by"
    impacted_by = "impacted_by"


class SimulationStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    warning = "warning"
    failed = "failed"
    blocked = "blocked"


class _Base(BaseModel):
    id: str
    organization_id: str
    workspace_id: str


class TwinEntity(_Base):
    entity_type: TwinEntityType
    external_ref: str = ""
    name: str
    summary: str = ""
    attributes: dict = Field(default_factory=dict)
    confidence: float = 0.5
    evidence_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)

    @field_validator("confidence")
    @classmethod
    def _c(cls, v: float) -> float:
        return min(max(v, 0.0), 1.0)


class TwinRelationship(_Base):
    source_entity_id: str
    target_entity_id: str
    relationship_type: TwinRelationshipType
    weight: float = 1.0
    confidence: float = 0.5
    evidence_ids: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class TwinSnapshot(_Base):
    name: str
    node_count: int
    edge_count: int
    summary: str = ""
    checksum: str
    created_at: datetime = Field(default_factory=_now)


class ImpactPropagationResult(_Base):
    source_entity_id: str
    impact_type: str
    affected_entities: list[dict] = Field(default_factory=list)
    impact_score: float = 0.0
    confidence: float = 0.5
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


class BlastRadiusResult(_Base):
    target_entity_id: str
    severity: str
    affected_domains: list[str] = Field(default_factory=list)
    affected_entities: list[dict] = Field(default_factory=list)
    mitigation_options: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    limitations: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)
