from app.content.models import ContentItem, PipelineRunResult


class ContentReportBuilder:
    def build_item_summary(self, item: ContentItem) -> dict:
        return {'content_id': item.id, 'topic': item.topic, 'brand': item.brand, 'platforms': [p.value for p in item.platforms], 'status': item.status.value, 'policy_passed': item.policy_passed}

    def build_pipeline_summary(self, result: PipelineRunResult) -> dict:
        return {'run_id': result.id, 'content_id': result.content_id, 'ok': result.ok, 'status': result.status.value, 'steps': result.steps, 'duration_ms': result.duration_ms}

    def build_markdown_report(self, item: ContentItem) -> str:
        return f"# Content Report\n\n- Content ID: {item.id}\n- Topic: {item.topic}\n- Brand: {item.brand}\n- Platforms: {', '.join([p.value for p in item.platforms])}\n- Status: {item.status.value}\n- Policy: {'passed' if item.policy_passed else 'failed'}\n- Draft: {item.draft_text}\n- Edited: {item.edited_text}\n- Graphic Prompt: {item.graphic_prompt}\n- Graphic Asset URL: {item.graphic_asset_url}\n- Scheduled At: {item.scheduled_at}\n- Posted At: {item.posted_at}\n- Safety Notes: {item.policy_notes}\n"
