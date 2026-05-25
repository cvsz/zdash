from app.agents.base import BaseAgent
from app.content.models import ApproveContentRequest, PublishContentRequest, ScheduleContentRequest
from app.content.pipeline import content_pipeline
from app.core.events import event_bus


class SocialAgent(BaseAgent):
    id = 'social'
    name = 'Social'
    role = 'social_publisher'

    def schedule_content(self, request: ScheduleContentRequest):
        event_bus.emit('social.command.received', self.id, 'schedule_content', {})
        item = content_pipeline.social.schedule_content(request)
        event_bus.emit('social.command.completed', self.id, 'schedule_content', {'content_id': item.id})
        return item

    def approve_content(self, request: ApproveContentRequest):
        item = content_pipeline.social.approve_content(request)
        return item

    def publish_content(self, request: PublishContentRequest):
        return content_pipeline.social.publish_content(request)

    def health_check(self): return {'id': self.id, 'status': 'idle'}
