from app.content.models import ContentItem, PipelineRunResult


class ContentReportBuilder:
    def build_item_summary(self, item: ContentItem) -> dict:
        return {
            "content_id": item.id,
            "topic": item.topic,
            "brand": item.brand,
            "platforms": [platform.value for platform in item.platforms],
            "status": item.status.value,
            "policy_passed": item.policy_passed,
            "policy_notes": item.policy_notes,
        }

    def build_pipeline_summary(self, result: PipelineRunResult) -> dict:
        return {
            "run_id": result.id,
            "content_id": result.content_id,
            "ok": result.ok,
            "status": result.status.value,
            "steps": result.steps,
            "duration_ms": result.duration_ms,
        }

    def build_markdown_report(self, item: ContentItem) -> str:
        platforms = ", ".join(platform.value for platform in item.platforms)
        policy = "passed" if item.policy_passed else "failed"

        return "\n".join(
            [
                "# Content Report",
                "",
                f"- Content ID: {item.id}",
                f"- Topic: {item.topic}",
                f"- Brand: {item.brand}",
                f"- Platforms: {platforms}",
                f"- Status: {item.status.value}",
                f"- Policy: {policy}",
                f"- Draft: {item.draft_text}",
                f"- Edited: {item.edited_text}",
                f"- Graphic Prompt: {item.graphic_prompt}",
                f"- Graphic Asset URL: {item.graphic_asset_url}",
                f"- Scheduled At: {item.scheduled_at}",
                f"- Approved At: {item.approved_at}",
                f"- Posted At: {item.posted_at}",
                f"- Safety Notes: {item.policy_notes}",
                "",
            ]
        )
