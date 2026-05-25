from __future__ import annotations

from app.content.image_adapters import ImageGenerationAdapter, MockImageGenerationAdapter
from app.content.models import ContentStatus, GraphicRequest
from app.content.store import InMemoryContentStore
from app.core.events import event_bus


class GraphicService:
    def __init__(self, store: InMemoryContentStore, adapter: ImageGenerationAdapter | None = None) -> None:
        self.store = store
        self.adapter = adapter or MockImageGenerationAdapter()

    def create_graphic_prompt(self, request: GraphicRequest):
        item = self.store.get_item(request.content_id)
        if item is None:
            raise ValueError('content not found')
        event_bus.emit('content.graphic.requested', 'GraphicService', 'Graphic requested', {'content_id': item.id})
        base = item.edited_text or item.draft_text or item.topic
        prompt = f'{request.style} | {request.aspect_ratio} | {base}'
        if request.instructions:
            prompt += f' | {request.instructions}'
        item = self.store.update_item(item.id, {'graphic_prompt': prompt, 'status': ContentStatus.graphic_requested})
        event_bus.emit('content.graphic.prompt.created', 'GraphicService', 'Graphic prompt created', {'content_id': item.id})
        return item

    def generate_graphic(self, request: GraphicRequest):
        item = self.create_graphic_prompt(request)
        try:
            result = self.adapter.generate_image(item.graphic_prompt or '', {'content_id': item.id})
            item = self.store.update_item(item.id, {'graphic_asset_url': result.get('asset_url'), 'status': ContentStatus.graphic_ready})
            event_bus.emit('content.graphic.generated', 'GraphicService', 'Graphic generated', {'content_id': item.id, 'result': result})
            return item
        except Exception as exc:
            self.store.update_item(item.id, {'status': ContentStatus.failed})
            event_bus.emit('content.graphic.failed', 'GraphicService', 'Graphic failed', {'content_id': item.id, 'error': str(exc)})
            raise
