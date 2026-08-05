from datetime import UTC, datetime

from app.content.models import ContentItem, ContentPlatform, ContentStatus, ContentType
from app.marketing.service import MarketingDashboardService


def make_item(
    item_id: str,
    status: ContentStatus,
    *,
    scheduled_at: datetime | None = None,
) -> ContentItem:
    return ContentItem(
        id=item_id,
        title=f"Content {item_id}",
        content_type=ContentType.educational,
        status=status,
        brand="zDash",
        language="en",
        tone="professional",
        topic="governed automation",
        platforms=[ContentPlatform.linkedin],
        scheduled_at=scheduled_at,
    )


def test_marketing_dashboard_uses_live_content_metrics_and_labelled_samples():
    scheduled_at = datetime(2026, 8, 6, 2, 0, tzinfo=UTC)
    dashboard = MarketingDashboardService(
        [
            make_item("draft", ContentStatus.draft),
            make_item("scheduled", ContentStatus.scheduled, scheduled_at=scheduled_at),
            make_item("posted", ContentStatus.posted),
        ]
    ).build()

    metrics = {metric.key: metric for metric in dashboard.metrics}
    assert metrics["content_assets"].value == 3
    assert metrics["awaiting_approval"].value == 2
    assert metrics["scheduled"].value == 1
    assert metrics["published"].value == 1
    assert all(metric.source == "live" for metric in dashboard.metrics)

    assert dashboard.schedule[0].id == "scheduled"
    assert dashboard.schedule[0].source == "live"
    assert dashboard.schedule[0].scheduled_for == scheduled_at.isoformat()

    assert dashboard.hooks
    assert dashboard.competitors
    assert dashboard.trends
    assert dashboard.campaign_recommendations
    assert all(item.source == "sample" for item in dashboard.hooks)
    assert all(item.source == "sample" for item in dashboard.competitors)
    assert all(item.source == "sample" for item in dashboard.trends)
    assert all(item.source == "sample" for item in dashboard.campaign_recommendations)
    assert "sample data" in dashboard.disclaimer


def test_marketing_dashboard_uses_labelled_calendar_samples_when_empty():
    dashboard = MarketingDashboardService([]).build()

    assert dashboard.metrics[0].value == 0
    assert dashboard.schedule
    assert all(item.source == "sample" for item in dashboard.schedule)
    assert dashboard.source_mode == "live_content_with_labelled_samples"
