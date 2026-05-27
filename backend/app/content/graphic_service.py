from __future__ import annotations

from app.content.image_adapters import (
    ImageGenerationAdapter,
    build_image_adapter,
)
from app.content.models import ContentStatus, GraphicRequest
from app.content.store import InMemoryContentStore
from app.core.config import get_settings
from app.core.events import event_bus


class GraphicService:
    def __init__(
        self, store: InMemoryContentStore, adapter: ImageGenerationAdapter | None = None
    ) -> None:
        self.store = store
        self.settings = get_settings()
        self.adapter = adapter or build_image_adapter()

    def create_graphic_prompt(self, request: GraphicRequest):
        item = self.store.get_item(request.content_id)
        if item is None:
            raise ValueError("content not found")
        self._emit_content_event(
            "content.graphic.requested",
            "GraphicService",
            "Graphic requested",
            {"content_id": item.id},
        )
        base = item.edited_text or item.draft_text or item.topic
        prompt = (
            f"{request.style} | {request.aspect_ratio} | brand={item.brand} | "
            f"tone={item.tone} | text={base}"
        )
        if request.instructions:
            prompt += f" | {request.instructions}"
        item = self.store.update_item(
            item.id,
            {"graphic_prompt": prompt, "status": ContentStatus.graphic_requested},
        )
        self._emit_content_event(
            "content.graphic.prompt.created",
            "GraphicService",
            "Graphic prompt created",
            {"content_id": item.id},
        )
        return item

    def generate_graphic(self, request: GraphicRequest):
        item = self.create_graphic_prompt(request)
        try:
            result = self.adapter.generate_image(
                item.graphic_prompt or "",
                {
                    "content_id": item.id,
                    "provider": self.settings.image_generation_provider,
                    "dry_run": self.settings.image_dry_run,
                    "output_dir": self.settings.image_output_dir,
                },
            )
            if not result.get("ok", False):
                raise ValueError(result.get("message", "graphic generation failed"))
            item = self.store.update_item(
                item.id,
                {
                    "graphic_asset_url": result.get("asset_url"),
                    "status": ContentStatus.graphic_ready,
                    "metadata": {
                        **item.metadata,
                        "image_generation": {
                            "provider": result.get("provider", "mock"),
                            "dry_run": result.get("dry_run", True),
                        },
                    },
                },
            )
            self._emit_content_event(
                "content.graphic.generated",
                "GraphicService",
                "Graphic generated",
                {"content_id": item.id, "result": result},
            )
            return item
        except Exception as exc:
            self.store.update_item(item.id, {"status": ContentStatus.failed})
            self._emit_content_event(
                "content.graphic.failed",
                "GraphicService",
                "Graphic failed",
                {"content_id": item.id, "error": str(exc)},
            )
            raise

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
