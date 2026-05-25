from app.agents.base import BaseAgent
from app.content.models import CreateContentRequest, EditContentRequest
from app.content.pipeline import content_pipeline
from app.core.events import event_bus


class EditorAgent(BaseAgent):
    id = 'editor'
    name = 'Editor'
    role = 'content_editor'

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
