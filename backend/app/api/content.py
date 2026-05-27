from __future__ import annotations

from fastapi import APIRouter, Depends

from app.auth.dependencies import require_authenticated, require_permission
from app.auth.rbac import Permission
from app.content.models import (
    ApproveContentRequest,
    ContentStatus,
    CreateContentRequest,
    EditContentRequest,
    GraphicRequest,
    PublishContentRequest,
    ScheduleContentRequest,
)
from app.content.pipeline import get_content_pipeline
from app.content.reports import ContentReportBuilder
from app.core.responses import fail, ok

router = APIRouter(prefix="/api/content", tags=["content"])
reports = ContentReportBuilder()


def _pipeline():
    return get_content_pipeline()


@router.get("/status")
def status(_: object = Depends(require_authenticated)):
    return ok(_pipeline().get_status())


@router.post("/create")
def create(
    req: CreateContentRequest,
    _: object = Depends(require_authenticated),
):
    try:
        return ok({"item": _pipeline().editor.create_draft(req).model_dump(mode="json")})
    except Exception as exc:
        return fail("CONTENT_CREATE_FAILED", str(exc))


@router.post("/edit")
def edit(
    req: EditContentRequest,
    _: object = Depends(require_authenticated),
):
    try:
        return ok({"item": _pipeline().editor.edit_content(req).model_dump(mode="json")})
    except Exception as exc:
        return fail("CONTENT_EDIT_FAILED", str(exc))


@router.post("/generate-graphic")
def generate_graphic(
    req: GraphicRequest,
    _: object = Depends(require_authenticated),
):
    try:
        item = _pipeline().graphic.generate_graphic(req)
        return ok({"item": item.model_dump(mode="json")})
    except Exception as exc:
        return fail("CONTENT_GRAPHIC_FAILED", str(exc))


@router.post("/schedule")
def schedule(
    req: ScheduleContentRequest,
    _: object = Depends(require_authenticated),
):
    try:
        item = _pipeline().social.schedule_content(req)
        return ok({"item": item.model_dump(mode="json")})
    except Exception as exc:
        return fail("CONTENT_SCHEDULE_FAILED", str(exc))


@router.post("/approve")
def approve(
    req: ApproveContentRequest,
    _: object = Depends(require_permission(Permission.MANAGE_CONTENT_APPROVAL)),
):
    try:
        item = _pipeline().social.approve_content(req)
        return ok({"item": item.model_dump(mode="json")})
    except Exception as exc:
        return fail("CONTENT_APPROVAL_FAILED", str(exc))


@router.post("/post")
def post(
    req: PublishContentRequest,
    _: object = Depends(require_permission(Permission.MANAGE_CONTENT_APPROVAL)),
):
    try:
        results = _pipeline().social.publish_content(req)
        return ok({"results": [result.model_dump(mode="json") for result in results]})
    except Exception as exc:
        return fail("CONTENT_PUBLISH_FAILED", str(exc))


@router.post("/pipeline/run")
def run(
    req: CreateContentRequest,
    _: object = Depends(require_authenticated),
):
    try:
        result = _pipeline().run_full_pipeline(req)
        return ok({"run": result.model_dump(mode="json")})
    except Exception as exc:
        return fail("CONTENT_PIPELINE_FAILED", str(exc))


@router.get("/items")
def items(
    status: ContentStatus | None = None,
    _: object = Depends(require_authenticated),
):
    items_payload = [i.model_dump(mode="json") for i in _pipeline().store.list_items(status)]
    return ok({"items": items_payload})


@router.get("/items/{content_id}")
def item(
    content_id: str,
    _: object = Depends(require_authenticated),
):
    found_item = _pipeline().store.get_item(content_id)
    if found_item is None:
        return fail("ITEM_NOT_FOUND", "Content item not found")
    return ok({"item": found_item.model_dump(mode="json")})


@router.get("/runs")
def runs(_: object = Depends(require_authenticated)):
    run_items = [r.model_dump(mode="json") for r in _pipeline().store.list_pipeline_runs()]
    return ok({"runs": run_items})


@router.get("/items/{content_id}/report")
def report(
    content_id: str,
    _: object = Depends(require_authenticated),
):
    found_item = _pipeline().store.get_item(content_id)
    if found_item is None:
        return fail("ITEM_NOT_FOUND", "Content item not found")
    return ok(
        {
            "summary": reports.build_item_summary(found_item),
            "markdown": reports.build_markdown_report(found_item),
            "logs": [
                entry.model_dump(mode="json")
                for entry in _pipeline().store.list_logs(content_id=content_id)
            ],
        }
    )
