from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class PlanTier(str, Enum):
    free='free'; starter='starter'; pro='pro'; enterprise='enterprise'
class SubscriptionStatus(str, Enum):
    trialing='trialing'; active='active'; past_due='past_due'; canceled='canceled'; expired='expired'; suspended='suspended'

@dataclass
class BillingPlan:
    id:str; tier:PlanTier; name:str; description:str; price_monthly:float; price_yearly:float|None; currency:str='USD'; features:list[str]=field(default_factory=list); limits:dict[str,Any]=field(default_factory=dict); is_public:bool=True; created_at:datetime=field(default_factory=utcnow); updated_at:datetime=field(default_factory=utcnow)

@dataclass
class EntitlementDecision:
    allowed:bool; feature:str; reason:str; plan_tier:str; required_tier:str|None=None; quota:dict[str,Any]|None=None; usage:dict[str,Any]|None=None; timestamp:datetime=field(default_factory=utcnow)
