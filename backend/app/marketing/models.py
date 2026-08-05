from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

DataSource = Literal["live", "sample"]
StageStatus = Literal["ready", "attention", "planned"]


class MarketingMetric(BaseModel):
    key: str
    label: str
    value: int | float | str
    detail: str
    source: DataSource = "live"


class MarketingStage(BaseModel):
    key: str
    label: str
    description: str
    status: StageStatus
    route: str | None = None


class HookInsight(BaseModel):
    id: str
    hook: str
    category: str
    usage_count: int = Field(ge=0)
    performance_note: str
    source: DataSource = "sample"


class CompetitorInsight(BaseModel):
    id: str
    name: str
    platform: str
    momentum: str
    opportunity: str
    source: DataSource = "sample"


class TrendInsight(BaseModel):
    id: str
    topic: str
    signal: str
    recommended_angle: str
    source: DataSource = "sample"


class ScheduleItem(BaseModel):
    id: str
    title: str
    platform: str
    scheduled_for: str
    status: str
    source: DataSource


class CampaignRecommendation(BaseModel):
    id: str
    campaign: str
    recommendation: str
    rationale: str
    approval_required: bool = True
    source: DataSource = "sample"


class MarketingDashboard(BaseModel):
    generated_at: datetime
    source_mode: str
    disclaimer: str
    metrics: list[MarketingMetric]
    system_map: list[MarketingStage]
    hooks: list[HookInsight]
    competitors: list[CompetitorInsight]
    trends: list[TrendInsight]
    schedule: list[ScheduleItem]
    campaign_recommendations: list[CampaignRecommendation]
