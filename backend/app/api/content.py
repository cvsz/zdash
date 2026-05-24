from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.content.pipeline import content_pipeline
from app.core.audit import audit
from app.core.auth import CurrentUser, require_roles
from app.core.observability import content_pipeline_action_total
from app.core.responses import fail, ok

router = APIRouter(prefix='/api/content', tags=['content'])


class CreateContentRequest(BaseModel):
    topic: str = Field(min_length=3)
    body: str = Field(min_length=3)


class ItemRefRequest(BaseModel):
    item_id: str


class ScheduleContentRequest(BaseModel):
    item_id: str
    schedule_at: str


@router.post('/create')
def create(req: CreateContentRequest, current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst'))):
    item = content_pipeline.create(req.topic, req.body)
    content_pipeline_action_total.labels(action='create').inc()
    return ok({'item': item})


@router.post('/generate-graphic')
def generate_graphic(req: ItemRefRequest, current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst'))):
    try:
        item = content_pipeline.generate_graphic(req.item_id)
    except KeyError:
        return fail('ITEM_NOT_FOUND', 'Content item not found')
    content_pipeline_action_total.labels(action='generate_graphic').inc()
    return ok({'item': item})


@router.post('/schedule')
def schedule(req: ScheduleContentRequest, current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst'))):
    try:
        item = content_pipeline.schedule(req.item_id, req.schedule_at)
    except KeyError:
        return fail('ITEM_NOT_FOUND', 'Content item not found')
    content_pipeline_action_total.labels(action='schedule').inc()
    return ok({'item': item})


@router.post('/approve')
def approve(req: ItemRefRequest, current_user: CurrentUser = Depends(require_roles('admin', 'operator'))):
    try:
        item = content_pipeline.approve(req.item_id)
    except KeyError:
        return fail('ITEM_NOT_FOUND', 'Content item not found')
    content_pipeline_action_total.labels(action='approve').inc()
    audit('content_approve', current_user.username, current_user.role, target=req.item_id)
    return ok({'item': item})


@router.post('/post')
def post(req: ItemRefRequest, current_user: CurrentUser = Depends(require_roles('admin', 'operator'))):
    try:
        item = content_pipeline.post(req.item_id)
    except KeyError:
        return fail('ITEM_NOT_FOUND', 'Content item not found')
    except ValueError as exc:
        return fail('APPROVAL_REQUIRED', str(exc))
    content_pipeline_action_total.labels(action='post').inc()
    audit('content_post', current_user.username, current_user.role, target=req.item_id, detail=item.get('post_result', {}))
    return ok({'item': item})


@router.get('/items')
def items(current_user: CurrentUser = Depends(require_roles('admin', 'operator', 'analyst', 'viewer'))):
    return ok({'items': content_pipeline.list_items()})
