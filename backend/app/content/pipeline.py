from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.core.config import get_settings
from app.core.database import session_scope
from app.core.events import event_bus
from app.repositories import Repository


class ContentPipeline:
    def __init__(self) -> None:
        self.settings = get_settings()

    def create(self, topic: str, body: str) -> dict[str, Any]:
        item_id = str(uuid4())
        item = {
            'id': item_id,
            'topic': topic,
            'body': body,
            'state': 'draft',
            'approved': False,
            'created_at': datetime.now(timezone.utc).isoformat(),
        }
        with session_scope() as session:
            Repository(session).add_content_item(item_id, topic, body, 'draft', False, item)
        event_bus.emit('content_action', 'ContentPipeline', {'action': 'create', 'item': item})
        return item

    def generate_graphic(self, item_id: str) -> dict[str, Any]:
        with session_scope() as session:
            repo = Repository(session)
            row = repo.get_content_item(item_id)
            if row is None:
                raise KeyError(item_id)
            payload = row.payload
            payload['graphic_url'] = f'mock://graphic/{item_id}'
            payload['state'] = 'graphic_ready'
            row = repo.update_content_item(item_id, state='graphic_ready', payload=payload)
            assert row is not None
            result = {
                'id': row.id,
                'topic': row.topic,
                'body': row.body,
                'state': row.state,
                'approved': row.approved,
                **row.payload,
            }
        event_bus.emit('content_action', 'ContentPipeline', {'action': 'generate_graphic', 'item_id': item_id})
        return result

    def schedule(self, item_id: str, schedule_at: str) -> dict[str, Any]:
        with session_scope() as session:
            repo = Repository(session)
            row = repo.get_content_item(item_id)
            if row is None:
                raise KeyError(item_id)
            payload = row.payload
            payload['schedule_at'] = schedule_at
            payload['state'] = 'scheduled'
            row = repo.update_content_item(item_id, state='scheduled', payload=payload)
            assert row is not None
            result = {'id': row.id, 'topic': row.topic, 'body': row.body, 'state': row.state, 'approved': row.approved, **row.payload}
        event_bus.emit('content_action', 'ContentPipeline', {'action': 'schedule', 'item_id': item_id})
        return result

    def approve(self, item_id: str) -> dict[str, Any]:
        with session_scope() as session:
            repo = Repository(session)
            row = repo.get_content_item(item_id)
            if row is None:
                raise KeyError(item_id)
            payload = row.payload
            payload['state'] = 'approved'
            row = repo.update_content_item(item_id, approved=True, state='approved', payload=payload)
            assert row is not None
            result = {'id': row.id, 'topic': row.topic, 'body': row.body, 'state': row.state, 'approved': row.approved, **row.payload}
        event_bus.emit('content_action', 'ContentPipeline', {'action': 'approve', 'item_id': item_id})
        return result

    def post(self, item_id: str) -> dict[str, Any]:
        with session_scope() as session:
            repo = Repository(session)
            row = repo.get_content_item(item_id)
            if row is None:
                raise KeyError(item_id)
            if self.settings.social_approval_required and not row.approved:
                raise ValueError('Approval required before posting.')

            payload = row.payload
            payload['post_result'] = {'dry_run': self.settings.social_dry_run, 'published': not self.settings.social_dry_run}
            payload['state'] = 'scheduled' if self.settings.social_dry_run else 'posted'
            row = repo.update_content_item(item_id, state=payload['state'], payload=payload)
            assert row is not None
            result = {'id': row.id, 'topic': row.topic, 'body': row.body, 'state': row.state, 'approved': row.approved, **row.payload}
        event_bus.emit('social_post_action', 'ContentPipeline', {'item_id': item_id, 'result': payload['post_result']})
        return result

    def list_items(self) -> list[dict[str, Any]]:
        with session_scope() as session:
            rows = Repository(session).list_content_items()
        return [
            {
                'id': r.id,
                'topic': r.topic,
                'body': r.body,
                'state': r.state,
                'approved': r.approved,
                **r.payload,
            }
            for r in rows
        ]


content_pipeline = ContentPipeline()
