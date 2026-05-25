from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import get_settings
from app.content.models import ApproveContentRequest, ContentStatus, PublishContentRequest, ScheduleContentRequest
from app.content.social_adapters import MockSocialMediaAdapter, SocialMediaAdapter
from app.content.store import InMemoryContentStore
from app.core.events import event_bus


class SocialService:
    def __init__(self, store: InMemoryContentStore, adapter: SocialMediaAdapter | None = None) -> None:
        self.store = store
        self.adapter = adapter or MockSocialMediaAdapter()
        self.settings = get_settings()

    def schedule_content(self, request: ScheduleContentRequest):
        item = self._require(request.content_id)
        patch = {'scheduled_at': request.scheduled_at, 'status': ContentStatus.scheduled}
        if request.platforms:
            patch['platforms'] = request.platforms
        item = self.store.update_item(item.id, patch)
        event_bus.emit('content.scheduled', 'SocialService', 'Content scheduled', {'content_id': item.id})
        return item

    def approve_content(self, request: ApproveContentRequest):
        item = self._require(request.content_id)
        if not item.policy_passed:
            event_bus.emit('content.rejected', 'SocialService', 'Approval blocked by policy', {'content_id': item.id})
            raise ValueError('policy check failed')
        item = self.store.update_item(item.id, {'status': ContentStatus.approved, 'approved_at': datetime.now(timezone.utc)})
        event_bus.emit('content.approved', 'SocialService', 'Content approved', {'content_id': item.id, 'approved_by': request.approved_by})
        return item

    def publish_content(self, request: PublishContentRequest):
        item = self._require(request.content_id)
        event_bus.emit('content.publish.requested', 'SocialService', 'Publish requested', {'content_id': item.id})
        if item.status in (ContentStatus.rejected, ContentStatus.failed):
            raise ValueError('cannot publish rejected or failed content')
        if not item.policy_passed:
            event_bus.emit('content.publish.blocked', 'SocialService', 'Policy failed', {'content_id': item.id})
            raise ValueError('policy check failed')
        if self.settings.social_approval_required and item.status != ContentStatus.approved:
            event_bus.emit('content.publish.blocked', 'SocialService', 'Approval required', {'content_id': item.id})
            raise ValueError('approval required')
        if not self.settings.social_dry_run and not request.confirmation:
            raise ValueError('confirmation required for real posting')
        results = []
        for p in (request.platforms or item.platforms):
            res = self.adapter.publish(p, item.edited_text or item.draft_text or item.topic, item.graphic_asset_url, item.metadata)
            results.append(res)
        event_bus.emit('content.publish.simulated' if self.settings.social_dry_run else 'content.published', 'SocialService', 'Publish complete', {'content_id': item.id})
        self.store.update_item(item.id, {'status': ContentStatus.posted if not self.settings.social_dry_run else item.status, 'posted_at': datetime.now(timezone.utc) if not self.settings.social_dry_run else item.posted_at})
        return results

    def _require(self, content_id: str):
        item = self.store.get_item(content_id)
        if item is None:
            raise ValueError('content not found')
        return item
