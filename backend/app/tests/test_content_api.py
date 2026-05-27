from datetime import datetime, timedelta, timezone

from app.api import content as content_api
from app.content.models import (
    ApproveContentRequest,
    CreateContentRequest,
    EditContentRequest,
    GraphicRequest,
    PublishContentRequest,
    ScheduleContentRequest,
)


def _assert_envelope(payload: dict) -> None:
    assert set(payload.keys()) == {"ok", "data", "error", "timestamp"}


def test_content_api_full_flow() -> None:
    status_body = content_api.status()
    _assert_envelope(status_body)
    assert status_body["ok"] is True

    create_body = content_api.create(
        CreateContentRequest(topic="Educational simulation market note")
    )
    _assert_envelope(create_body)
    assert create_body["ok"] is True
    content_id = create_body["data"]["item"]["id"]

    edit_body = content_api.edit(
        EditContentRequest(content_id=content_id, instructions="Shorten copy")
    )
    _assert_envelope(edit_body)
    assert edit_body["ok"] is True

    graphic_body = content_api.generate_graphic(GraphicRequest(content_id=content_id))
    _assert_envelope(graphic_body)
    assert graphic_body["ok"] is True

    schedule_body = content_api.schedule(
        ScheduleContentRequest(
            content_id=content_id,
            scheduled_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
    )
    _assert_envelope(schedule_body)
    assert schedule_body["ok"] is True

    approve_body = content_api.approve(ApproveContentRequest(content_id=content_id))
    _assert_envelope(approve_body)
    assert approve_body["ok"] is True

    post_body = content_api.post(PublishContentRequest(content_id=content_id))
    _assert_envelope(post_body)
    assert post_body["ok"] is True
    assert post_body["data"]["results"]

    items_body = content_api.items()
    _assert_envelope(items_body)
    assert items_body["ok"] is True
    assert items_body["data"]["items"]

    item_body = content_api.item(content_id)
    _assert_envelope(item_body)
    assert item_body["ok"] is True
    assert item_body["data"]["item"]["id"] == content_id

    report_body = content_api.report(content_id)
    _assert_envelope(report_body)
    assert report_body["ok"] is True
    assert "markdown" in report_body["data"]
    assert "summary" in report_body["data"]


def test_content_api_pipeline_run_and_runs_list() -> None:
    run_body = content_api.run(
        CreateContentRequest(topic="zDash weekly system update educational simulation")
    )
    _assert_envelope(run_body)
    assert run_body["ok"] is True
    run_id = run_body["data"]["run"]["id"]
    assert run_id

    runs_body = content_api.runs()
    _assert_envelope(runs_body)
    assert runs_body["ok"] is True
    assert runs_body["data"]["runs"]


def test_content_api_not_found_paths() -> None:
    missing_item = content_api.item("missing-content-id")
    _assert_envelope(missing_item)
    assert missing_item["ok"] is False
    assert missing_item["error"]["code"] == "ITEM_NOT_FOUND"

    missing_report = content_api.report("missing-content-id")
    _assert_envelope(missing_report)
    assert missing_report["ok"] is False
    assert missing_report["error"]["code"] == "ITEM_NOT_FOUND"
