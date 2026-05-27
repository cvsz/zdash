from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc)


class MacroScenarioType(str, Enum):
    base_case = "base_case"
    growth = "growth"
    downturn = "downturn"
    competitive_pressure = "competitive_pressure"
    regulatory_shift = "regulatory_shift"
    regional_expansion = "regional_expansion"
    supply_constraint = "supply_constraint"
    demand_spike = "demand_spike"
    custom = "custom"


class ShockType(str, Enum):
    market = "market"
    partner = "partner"
    infrastructure = "infrastructure"
    regulatory = "regulatory"
    pricing = "pricing"
    demand = "demand"
    supply = "supply"
    security = "security"
    reputation = "reputation"


class MacroScenario(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    name: str
    scenario_type: MacroScenarioType
    horizon: str = "12m"
    assumptions: list[str] = Field(default_factory=list)
    inputs: dict = Field(default_factory=dict)
    confidence: float = 0.5
    created_by: str = "system"
    created_at: datetime = Field(default_factory=now)
