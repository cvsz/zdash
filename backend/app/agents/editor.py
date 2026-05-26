from typing import Any

from app.agents.base import AgentMessage, BaseAgent
from app.content.models import CreateContentRequest, EditContentRequest
from app.content.pipeline import content_pipeline
from app.core.events import event_bus


class EditorAgent(BaseAgent):
    id = 'editor'
    name = 'Editor'
    role = 'content_editor'

    def __init__(self) -> None:
        super().__init__(agent_id=self.id, name=self.name, role=self.role)

    def receive_message(self, message: AgentMessage) -> dict[str, Any]:
        self.emit_event(
            'agent.message.received',
            'Editor agent received message',
            {'from_agent': message.from_agent, 'message': message.message},
        )
        return {'response_text': 'Editor agent is ready.', 'agent': self.id}

    def run_task(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        self.emit_event('agent.task.run', 'Editor task requested', {'task': task, 'context': context or {}})
        return {'ok': True, 'agent': self.id, 'task': task, 'dry_run': True}

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
