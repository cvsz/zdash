from fastapi import APIRouter

from app.content.models import ApproveContentRequest, ContentStatus, CreateContentRequest, EditContentRequest, GraphicRequest, PublishContentRequest, ScheduleContentRequest
from app.content.pipeline import content_pipeline
from app.content.reports import ContentReportBuilder
from app.core.responses import fail, ok

router = APIRouter(prefix='/api/content', tags=['content'])


@router.get('/status')
def status():
    s = content_pipeline.social.settings
    return ok({'enabled': True, 'store_type': 'in_memory', 'social_dry_run': s.social_dry_run, 'approval_required': s.social_approval_required, 'auto_post_enabled': s.social_auto_post_enabled, 'item_count': len(content_pipeline.store.list_items()), 'pipeline_run_count': len(content_pipeline.store.list_pipeline_runs())})

@router.post('/create')
def create(req: CreateContentRequest): return ok(content_pipeline.editor.create_draft(req).model_dump())
@router.post('/edit')
def edit(req: EditContentRequest): return ok(content_pipeline.editor.edit_content(req).model_dump())
@router.post('/generate-graphic')
def gen(req: GraphicRequest): return ok(content_pipeline.graphic.generate_graphic(req).model_dump())
@router.post('/schedule')
def schedule(req: ScheduleContentRequest): return ok(content_pipeline.social.schedule_content(req).model_dump())
@router.post('/approve')
def approve(req: ApproveContentRequest):
    try: return ok(content_pipeline.social.approve_content(req).model_dump())
    except ValueError as exc: return fail('APPROVAL_BLOCKED', str(exc))
@router.post('/post')
def post(req: PublishContentRequest):
    try: return ok([r.model_dump() for r in content_pipeline.social.publish_content(req)])
    except ValueError as exc: return fail('PUBLISH_BLOCKED', str(exc))
@router.post('/pipeline/run')
def run(req: CreateContentRequest): return ok(content_pipeline.run_full_pipeline(req).model_dump())
@router.get('/items')
def items(status: ContentStatus | None = None): return ok([i.model_dump() for i in content_pipeline.store.list_items(status)])
@router.get('/items/{content_id}')
def item(content_id: str):
    i = content_pipeline.store.get_item(content_id)
    return ok(i.model_dump()) if i else fail('ITEM_NOT_FOUND', 'Content item not found')
@router.get('/runs')
def runs(): return ok([r.model_dump() for r in content_pipeline.store.list_pipeline_runs()])
@router.get('/items/{content_id}/report')
def report(content_id: str):
    i = content_pipeline.store.get_item(content_id)
    if not i: return fail('ITEM_NOT_FOUND', 'Content item not found')
    rb = ContentReportBuilder()
    return ok({'markdown': rb.build_markdown_report(i), 'summary': rb.build_item_summary(i)})
