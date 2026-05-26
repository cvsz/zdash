from typing import Any

from app.agents.base import AgentMessage, BaseAgent
from app.content.models import CreateContentRequest, EditContentRequest
from app.content.pipeline import content_pipeline
from app.core.events import event_bus


class EditorAgent(BaseAgent):
    id = 'editor'
    name = 'Editor'
    role = 'content_editor'

    def receive_message(self, message: AgentMessage) -> dict[str, Any]:
        response = self.run_task(task=message.message, context=message.context)
        return {
            'to': message.from_agent,
            'from': self.id,
            'response': response,
        }

    def run_task(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        ctx = context or {}
        task_key = task.strip().lower()

        if task_key == 'health_check':
            return self.health_check()

        if task_key == 'create_draft':
            request = CreateContentRequest(**ctx)
            item = self.create_draft(request)
            return {'ok': True, 'content_id': item.id, 'status': item.status}

        if task_key == 'edit_content':
            request = EditContentRequest(**ctx)
            item = self.edit_content(request)
            return {'ok': True, 'content_id': item.id, 'status': item.status}

        if task_key == 'generate_variants':
            content_id = str(ctx.get('content_id', '')).strip()
            count = int(ctx.get('count', 1))
            variants = self.generate_variants(content_id=content_id, count=count)
            return {'ok': True, 'content_id': content_id, 'variants': variants}

        return {'ok': False, 'error': f'unsupported_task:{task}'}

    def create_draft(self, request: CreateContentRequest):
        event_bus.emit('editor.command.received', self.id, 'create_draft', {})
        item = content_pipeline.editor.create_draft(request)
        event_bus.emit('editor.command.completed', self.id, 'create_draft', {'content_id': item.id})
        return item

    def edit_content(self, request: EditContentRequest):
        event_bus.emit('editor.command.received', self.id, 'edit_content', {})
        item = content_pipeline.editor.edit_content(request)
        event_bus.emit('editor.command.completed', self.id, 'edit_content', {'content_id': item.id})
        return item

    def generate_variants(self, content_id: str, count: int):
        return content_pipeline.editor.generate_variants(content_id, count)

    def health_check(self):
        return {'id': self.id, 'status': 'idle'}
