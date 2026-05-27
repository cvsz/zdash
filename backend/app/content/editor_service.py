from __future__ import annotations

from typing import Any, Callable, cast

from app.content.models import ContentItem, CreateContentRequest, EditContentRequest
from app.content.policy import ContentPolicyChecker
from app.content.store import InMemoryContentStore
from app.core.config import get_settings
from app.core.events import event_bus


TRADING_DISCLAIMER = (
    "Educational simulation only. Not financial advice. "
    "Backtest results are not guaranteed future performance."
)


class EditorService:
    def __init__(
        self,
        store: InMemoryContentStore,
        policy: ContentPolicyChecker | None = None,
        text_generator: Callable[[str], str] | None = None,
    ) -> None:
        self.store = store
        self.policy = policy or ContentPolicyChecker()
        self.settings = get_settings()
        self.text_generator = text_generator

    def create_draft(self, request: CreateContentRequest):
        item = self.store.create_item(request)
        draft = self._generate_draft_text(item)
        draft = self._ensure_trading_disclaimer(draft)
        item = self.store.update_item(item.id, {"draft_text": draft})
        self._emit_content_event(
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
        src = str(item.draft_text or item.topic)
        edited = f"{src} Refined for clarity and readability."
        if request.instructions:
            edited += f" Instructions: {request.instructions}."
        edited = self._ensure_trading_disclaimer(edited)
        patch = {
            "edited_text": edited,
            "status": "edited",
            "tone": request.tone or item.tone,
            "language": request.language or item.language,
        }
        item = self.store.update_item(item.id, patch)
        self._emit_content_event(
            "content.edited", "EditorService", "Content edited", {"content_id": item.id}
        )
        return self._check_policy(item.id, edited)

    def generate_variants(self, content_id: str, count: int = 3) -> list[str]:
        item = self.store.get_item(content_id)
        if item is None:
            raise ValueError("content not found")
        safe_count = max(1, min(count, 10))
        base = str(item.edited_text or item.draft_text or item.topic)
        variants = [
            self._ensure_trading_disclaimer(f"{base} (variant {index + 1})")
            for index in range(safe_count)
        ]
        for index, variant in enumerate(variants, start=1):
            self._emit_content_event(
                "content.variant.generated",
                "EditorService",
                "Variant generated",
                {"content_id": content_id, "variant_index": index, "variant": variant},
            )
        return variants

    def _check_policy(self, content_id: str, text: str):
        if not self.settings.content_require_policy_check:
            result: dict[str, Any] = {
                "passed": True,
                "notes": ["policy_check_disabled"],
                "blocked_terms": [],
                "warnings": [],
            }
        else:
            result = cast(dict[str, Any], self.policy.check_text(text, {"content_id": content_id}))
        notes = cast(list[str], result["notes"])
        warnings = cast(list[str], result["warnings"])
        self._emit_content_event(
            "content.policy.checked",
            "EditorService",
            "Policy checked",
            {"content_id": content_id, **result},
        )
        if not result["passed"]:
            self._emit_content_event(
                "content.policy.failed",
                "EditorService",
                "Policy failed",
                {"content_id": content_id, **result},
            )
        return self.store.update_item(
            content_id,
            {
                "policy_passed": result["passed"],
                "policy_notes": notes + warnings,
            },
        )

    def _generate_draft_text(self, item: ContentItem) -> str:
        deterministic_prompt = (
            f"[{item.brand}] {item.content_type.value}: {item.topic}. "
            f"Tone={item.tone}. Language={item.language}."
        )
        if self.text_generator is None:
            return deterministic_prompt
        try:
            generated = self.text_generator(deterministic_prompt)
        except Exception:
            return deterministic_prompt
        normalized = (generated or "").strip()
        return normalized if normalized else deterministic_prompt

    def _ensure_trading_disclaimer(self, text: str) -> str:
        lower = text.lower()
        if any(
            keyword in lower
            for keyword in ("trading", "market", "strategy", "backtest", "results")
        ) and TRADING_DISCLAIMER.lower() not in lower:
            return f"{text} {TRADING_DISCLAIMER}"
        return text

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
