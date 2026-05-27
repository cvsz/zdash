from __future__ import annotations

from app.content.models import CreateContentRequest, EditContentRequest
from app.content.policy import ContentPolicyChecker
from app.content.store import InMemoryContentStore
from app.core.events import event_bus


class EditorService:
    def __init__(
        self, store: InMemoryContentStore, policy: ContentPolicyChecker | None = None
    ) -> None:
        self.store = store
        self.policy = policy or ContentPolicyChecker()

    def create_draft(self, request: CreateContentRequest):
        item = self.store.create_item(request)
        draft = f"[{item.brand}] {item.topic} ({item.content_type.value}) - tone={item.tone}, lang={item.language}."
        if "trad" in item.topic.lower() or "market" in item.topic.lower():
            draft += " Educational simulation only. Not financial advice."
        item = self.store.update_item(item.id, {"draft_text": draft})
        event_bus.emit(
            "content.draft.created",
            "EditorService",
            "Draft created",
            {"content_id": item.id},
        )
        return self._check_policy(item.id, draft)

    def edit_content(self, request: EditContentRequest):
        item = self.store.get_item(request.content_id)
        if item is None:
            raise ValueError("content not found")
        src = item.draft_text or item.topic
        edited = f"{src} Refined for clarity."
        if request.instructions:
            edited += f" Instructions: {request.instructions}."
        if (
            "trad" in edited.lower()
            or "market" in edited.lower()
            or "backtest" in edited.lower()
        ):
            edited += " Educational use only. Past performance does not guarantee future results."
        patch = {
            "edited_text": edited,
            "status": "edited",
            "tone": request.tone or item.tone,
            "language": request.language or item.language,
        }
        item = self.store.update_item(item.id, patch)
        event_bus.emit(
            "content.edited", "EditorService", "Content edited", {"content_id": item.id}
        )
        return self._check_policy(item.id, edited)

    def generate_variants(self, content_id: str, count: int = 3) -> list[str]:
        item = self.store.get_item(content_id)
        if item is None:
            raise ValueError("content not found")
        base = item.edited_text or item.draft_text or item.topic
        variants = [f"{base} (variant {i + 1})" for i in range(count)]
        for _ in variants:
            event_bus.emit(
                "content.variant.generated",
                "EditorService",
                "Variant generated",
                {"content_id": content_id},
            )
        return variants

    def _check_policy(self, content_id: str, text: str):
        result = self.policy.check_text(text)
        event_bus.emit(
            "content.policy.checked",
            "EditorService",
            "Policy checked",
            {"content_id": content_id, **result},
        )
        if not result["passed"]:
            event_bus.emit(
                "content.policy.failed",
                "EditorService",
                "Policy failed",
                {"content_id": content_id, **result},
            )
        return self.store.update_item(
            content_id,
            {
                "policy_passed": result["passed"],
                "policy_notes": result["notes"] + result["warnings"],
            },
        )
