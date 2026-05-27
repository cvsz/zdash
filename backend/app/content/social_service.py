from __future__ import annotations

from datetime import datetime, timezone

from app.content.models import (
    ApproveContentRequest,
    ContentPlatform,
    ContentStatus,
    PublishContentRequest,
    ScheduleContentRequest,
)
from app.content.social_adapters import (
    MockSocialMediaAdapter,
    SocialMediaAdapter,
    build_platform_adapters,
)
from app.content.store import InMemoryContentStore
from app.core.config import get_settings
from app.core.events import event_bus


class SocialService:
    def __init__(
        self,
        store: InMemoryContentStore,
        adapter: SocialMediaAdapter | None = None,
        platform_adapters: dict[ContentPlatform, SocialMediaAdapter] | None = None,
    ) -> None:
        self.store = store
        self.settings = get_settings()
        self.adapter = adapter or MockSocialMediaAdapter()
        self.platform_adapters = platform_adapters or build_platform_adapters(
            self.settings
        )

    def schedule_content(self, request: ScheduleContentRequest):
        item = self._require(request.content_id)
        patch = {
            "scheduled_at": request.scheduled_at,
            "status": ContentStatus.scheduled,
        }
        if request.platforms:
            patch["platforms"] = request.platforms
        item = self.store.update_item(item.id, patch)
        self._emit_content_event(
            "content.scheduled",
            "SocialService",
            "Content scheduled",
            {"content_id": item.id},
        )
        return item

    def approve_content(self, request: ApproveContentRequest):
        item = self._require(request.content_id)
        if not item.policy_passed:
            rejected_item = self.store.update_item(
                item.id, {"status": ContentStatus.rejected}
            )
            self._emit_content_event(
                "content.rejected",
                "SocialService",
                "Approval blocked by policy",
                {"content_id": rejected_item.id},
            )
            raise ValueError("policy check failed")
        if item.status in (ContentStatus.failed, ContentStatus.rejected):
            self._emit_content_event(
                "content.rejected",
                "SocialService",
                "Approval blocked by content status",
                {"content_id": item.id, "status": item.status.value},
            )
            raise ValueError("cannot approve rejected or failed content")
        item = self.store.update_item(
            item.id,
            {
                "status": ContentStatus.approved,
                "approved_at": datetime.now(timezone.utc),
            },
        )
        self._emit_content_event(
            "content.approved",
            "SocialService",
            "Content approved",
            {
                "content_id": item.id,
                "approved_by": request.approved_by,
                "notes": request.notes,
            },
        )
        return item

    def publish_content(self, request: PublishContentRequest):
        item = self._require(request.content_id)
        self._emit_content_event(
            "content.publish.requested",
            "SocialService",
            "Publish requested",
            {"content_id": item.id},
        )
        if item.status in (ContentStatus.rejected, ContentStatus.failed):
            raise ValueError("cannot publish rejected or failed content")
        if not item.policy_passed:
            self._emit_content_event(
                "content.publish.blocked",
                "SocialService",
                "Policy failed",
                {"content_id": item.id},
            )
            raise ValueError("policy check failed")
        if (
            self.settings.social_approval_required
            and item.status != ContentStatus.approved
        ):
            self._emit_content_event(
                "content.publish.blocked",
                "SocialService",
                "Approval required",
                {"content_id": item.id},
            )
            raise ValueError("approval required")

        if not self.settings.social_dry_run:
            if not self.settings.social_auto_post_enabled:
                self._emit_content_event(
                    "content.publish.blocked",
                    "SocialService",
                    "Auto-post is disabled",
                    {"content_id": item.id},
                )
                raise ValueError("social auto-post is disabled")
            if not request.confirmation:
                self._emit_content_event(
                    "content.publish.blocked",
                    "SocialService",
                    "Confirmation missing for real publishing",
                    {"content_id": item.id},
                )
                raise ValueError("confirmation required for real posting")

        platforms = request.platforms or item.platforms
        if not platforms:
            raise ValueError("no target platforms configured")

        post_text = (item.edited_text or item.draft_text or item.topic).strip()
        if not post_text:
            raise ValueError("content text is empty")

        results = []
        try:
            for platform in platforms:
                adapter = self._resolve_adapter(platform)
                result = adapter.publish(
                    platform=platform,
                    text=post_text,
                    asset_url=item.graphic_asset_url,
                    metadata={"content_id": item.id, **item.metadata},
                )
                results.append(result)
                if not self.settings.social_dry_run and not result.ok:
                    raise ValueError(
                        f"real publishing blocked for {platform.value}: {result.message}"
                    )
        except Exception as exc:
            self._emit_content_event(
                "content.publish.failed",
                "SocialService",
                "Publish failed",
                {"content_id": item.id, "error": str(exc)},
            )
            raise

        event_type = (
            "content.publish.simulated"
            if self.settings.social_dry_run
            else "content.published"
        )
        self._emit_content_event(
            event_type,
            "SocialService",
            "Publish complete",
            {"content_id": item.id, "platform_count": len(platforms)},
        )
        if not self.settings.social_dry_run:
            self.store.update_item(
                item.id,
                {
                    "status": ContentStatus.posted,
                    "posted_at": datetime.now(timezone.utc),
                },
            )
        return results

    def _require(self, content_id: str):
        item = self.store.get_item(content_id)
        if item is None:
            raise ValueError("content not found")
        return item

    def _resolve_adapter(self, platform: ContentPlatform) -> SocialMediaAdapter:
        if (
            self.settings.social_dry_run
            or self.settings.social_provider.lower() == "mock"
        ):
            return self.adapter
        return self.platform_adapters.get(platform, self.adapter)

    def _emit_content_event(
        self, event_type: str, source: str, message: str, payload: dict
    ) -> None:
        event_bus.emit(event_type, source, message, payload)
        content_id = str(payload.get("content_id", "")).strip()
        if content_id:
            self.store.record_log(
                content_id=content_id,
                event_type=event_type,
                source=source,
                message=message,
                payload=payload,
            )
