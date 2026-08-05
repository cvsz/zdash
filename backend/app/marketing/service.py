from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from app.content.models import ContentItem
from app.content.pipeline import get_content_pipeline
from app.marketing.models import (
    CampaignRecommendation,
    CompetitorInsight,
    HookInsight,
    MarketingDashboard,
    MarketingMetric,
    MarketingStage,
    ScheduleItem,
    TrendInsight,
)


class MarketingDashboardService:
    """Build a read-only marketing operations snapshot.

    Content lifecycle metrics are derived from the existing content pipeline.
    External competitor, trend, and advertising connectors are not configured in
    this slice, so those insights are explicitly labelled as sample data.
    """

    def __init__(self, content_items: Iterable[ContentItem] | None = None) -> None:
        self._content_items = content_items

    def _items(self) -> list[ContentItem]:
        if self._content_items is not None:
            return list(self._content_items)
        return list(get_content_pipeline().store.list_items())

    def build(self) -> MarketingDashboard:
        items = self._items()
        scheduled = [item for item in items if item.status == "scheduled"]
        awaiting_approval = [
            item
            for item in items
            if item.approval_required
            and item.status not in {"approved", "posted", "rejected"}
        ]
        published = [item for item in items if item.status == "posted"]

        schedule = [
            ScheduleItem(
                id=item.id,
                title=item.title,
                platform=", ".join(item.platforms) if item.platforms else "unassigned",
                scheduled_for=(
                    item.scheduled_at.isoformat()
                    if item.scheduled_at is not None
                    else "not scheduled"
                ),
                status=str(item.status),
                source="live",
            )
            for item in scheduled[:6]
        ]
        if not schedule:
            schedule = [
                ScheduleItem(
                    id="sample-calendar-1",
                    title="AI operations field note",
                    platform="LinkedIn",
                    scheduled_for="Connect a publishing provider to schedule",
                    status="sample",
                    source="sample",
                ),
                ScheduleItem(
                    id="sample-calendar-2",
                    title="Safety-first automation short",
                    platform="TikTok / Shorts",
                    scheduled_for="Create and approve content in Content Pipeline",
                    status="sample",
                    source="sample",
                ),
            ]

        return MarketingDashboard(
            generated_at=datetime.now(UTC),
            source_mode="live_content_with_labelled_samples",
            disclaimer=(
                "Content lifecycle metrics use the local zDash content pipeline. "
                "Competitor, trend, hook-performance, and advertising insights are "
                "sample data until their provider connectors are configured."
            ),
            metrics=[
                MarketingMetric(
                    key="content_assets",
                    label="Content assets",
                    value=len(items),
                    detail="Items currently stored in the content pipeline",
                ),
                MarketingMetric(
                    key="awaiting_approval",
                    label="Awaiting approval",
                    value=len(awaiting_approval),
                    detail="Approval-gated items not yet approved or rejected",
                ),
                MarketingMetric(
                    key="scheduled",
                    label="Scheduled",
                    value=len(scheduled),
                    detail="Items with scheduled status",
                ),
                MarketingMetric(
                    key="published",
                    label="Published",
                    value=len(published),
                    detail="Items recorded as posted by the pipeline",
                ),
            ],
            system_map=[
                MarketingStage(
                    key="sources",
                    label="Sources & connectors",
                    description="Brand context, platform metrics, trends, and competitor feeds",
                    status="attention",
                    route="/settings",
                ),
                MarketingStage(
                    key="intelligence",
                    label="Marketing intelligence",
                    description="Turn signals into hooks, opportunities, and recommended actions",
                    status="ready",
                    route="/marketing",
                ),
                MarketingStage(
                    key="production",
                    label="Content production",
                    description="Create, edit, generate graphics, and apply policy checks",
                    status="ready",
                    route="/content",
                ),
                MarketingStage(
                    key="approval",
                    label="Human approval",
                    description="Review publishing and campaign changes before mutation",
                    status="ready",
                    route="/content",
                ),
                MarketingStage(
                    key="distribution",
                    label="Scheduling & distribution",
                    description="Queue approved content through platform adapters",
                    status="ready",
                    route="/scheduler",
                ),
                MarketingStage(
                    key="learning",
                    label="Performance learning",
                    description="Feed measured outcomes into the next content cycle",
                    status="planned",
                ),
            ],
            hooks=[
                HookInsight(
                    id="hook-1",
                    hook="The workflow looked efficient—until we measured the approval bottleneck.",
                    category="contrarian",
                    usage_count=0,
                    performance_note="Sample candidate; no connected performance history",
                ),
                HookInsight(
                    id="hook-2",
                    hook="Three controls that keep AI automation useful without giving up oversight.",
                    category="list",
                    usage_count=0,
                    performance_note="Sample candidate; validate against your audience",
                ),
                HookInsight(
                    id="hook-3",
                    hook="We rebuilt content operations as an auditable system, not a prompt collection.",
                    category="build",
                    usage_count=0,
                    performance_note="Sample candidate; attach real channel analytics before ranking",
                ),
            ],
            competitors=[
                CompetitorInsight(
                    id="competitor-1",
                    name="Operations educator archetype",
                    platform="LinkedIn",
                    momentum="Sample: process breakdowns",
                    opportunity="Show approval, audit, and failure recovery instead of generic AI tips",
                ),
                CompetitorInsight(
                    id="competitor-2",
                    name="Automation creator archetype",
                    platform="TikTok / Shorts",
                    momentum="Sample: rapid tool demonstrations",
                    opportunity="Differentiate with production architecture and measurable safeguards",
                ),
            ],
            trends=[
                TrendInsight(
                    id="trend-1",
                    topic="Human-in-the-loop automation",
                    signal="Sample signal",
                    recommended_angle="Demonstrate where approval gates prevent irreversible actions",
                ),
                TrendInsight(
                    id="trend-2",
                    topic="AI operations dashboards",
                    signal="Sample signal",
                    recommended_angle="Explain the system map from source data to audited publishing",
                ),
                TrendInsight(
                    id="trend-3",
                    topic="Content repurposing workflows",
                    signal="Sample signal",
                    recommended_angle="Show one approved source becoming platform-specific variants",
                ),
            ],
            schedule=schedule,
            campaign_recommendations=[
                CampaignRecommendation(
                    id="campaign-1",
                    campaign="Connected campaign required",
                    recommendation="Keep budget changes disabled",
                    rationale="No live advertising connector or verified spend/return data is available",
                ),
                CampaignRecommendation(
                    id="campaign-2",
                    campaign="Measurement baseline",
                    recommendation="Connect analytics before optimization",
                    rationale="Recommendations should use attributed conversions and cost data",
                ),
            ],
        )
