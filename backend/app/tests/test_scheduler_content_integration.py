from app.content.models import ContentStatus
from app.content.pipeline import get_content_pipeline
from app.scheduler.scheduler_service import get_scheduler_service


def _find_job_id_by_name(name: str) -> str:
    scheduler = get_scheduler_service()
    for job in scheduler.list_jobs():
        if job.name == name:
            return job.id
    raise AssertionError(f"Missing scheduler job: {name}")


def test_scheduler_content_job_calls_content_pipeline() -> None:
    scheduler = get_scheduler_service()
    content_job_id = _find_job_id_by_name("content_pipeline")

    pipeline = get_content_pipeline()
    assert len(pipeline.store.list_pipeline_runs()) == 0

    result = scheduler.run_job(content_job_id, manual=True)
    assert result.ok is True
    assert result.status == "completed"
    assert result.output["job_type"] == "content_pipeline"
    assert result.output["pipeline_run_id"]
    assert len(pipeline.store.list_pipeline_runs()) == 1


def test_scheduler_content_job_returns_pipeline_summary() -> None:
    scheduler = get_scheduler_service()
    content_job_id = _find_job_id_by_name("content_pipeline")
    result = scheduler.run_job(content_job_id, manual=True)
    assert "content_id" in result.output
    assert "content_status" in result.output
    assert "steps" in result.output
    assert result.output["auto_approved"] is False
    assert result.output["auto_published"] is False


def test_scheduler_content_job_does_not_approve_or_publish_automatically() -> None:
    scheduler = get_scheduler_service()
    content_job_id = _find_job_id_by_name("content_pipeline")
    pipeline = get_content_pipeline()

    result = scheduler.run_job(content_job_id, manual=True)
    item = pipeline.store.get_item(result.output["content_id"])
    assert item is not None
    assert item.status != ContentStatus.approved
    assert item.status != ContentStatus.posted
