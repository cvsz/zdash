from app.agents.base import BaseAgent
from app.content.models import GraphicRequest
from app.content.pipeline import content_pipeline
from app.core.events import event_bus


class GraphicAgent(BaseAgent):
    id = 'graphic'
    name = 'Graphic'
    role = 'creative_designer'

    def create_graphic_prompt(self, request: GraphicRequest):
        event_bus.emit('graphic.command.received', self.id, 'create_graphic_prompt', {})
        item = content_pipeline.graphic.create_graphic_prompt(request)
        event_bus.emit('graphic.command.completed', self.id, 'create_graphic_prompt', {'content_id': item.id})
        return item

    def generate_graphic(self, request: GraphicRequest):
        event_bus.emit('graphic.command.received', self.id, 'generate_graphic', {})
        item = content_pipeline.graphic.generate_graphic(request)
        event_bus.emit('graphic.command.completed', self.id, 'generate_graphic', {'content_id': item.id})
        return item

    def health_check(self): return {'id': self.id, 'status': 'idle'}
