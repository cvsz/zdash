from __future__ import annotations

from fastapi import APIRouter

from app.core.observability import scheduler_job_total
from app.core.responses import fail, ok
from app.scheduler import CreateJobRequest
from app.scheduler.job_store import JobNotFoundError
from app.scheduler.scheduler_service import get_scheduler_service

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


def _service():
    return get_scheduler_service()


@router.get("/status")
def status() -> dict:
    return ok({"scheduler": _service().get_status()})


@router.get("/jobs")
def list_jobs() -> dict:
    jobs = [job.model_dump(mode="json") for job in _service().list_jobs()]
    return ok({"jobs": jobs})


@router.post("/jobs")
def create_job(req: CreateJobRequest) -> dict:
    try:
        job = _service().create_job(req)
    except ValueError as exc:
        return fail("SCHEDULER_JOB_INVALID", str(exc))
    scheduler_job_total.labels(action="create").inc()
    return ok({"job": job.model_dump(mode="json")})


@router.post("/jobs/{job_id}/run")
def run_job(job_id: str) -> dict:
    try:
        result = _service().run_job(job_id, manual=True)
    except JobNotFoundError as exc:
        return fail("SCHEDULER_JOB_NOT_FOUND", str(exc))
    except Exception as exc:
        return fail("SCHEDULER_JOB_RUN_FAILED", str(exc))
    scheduler_job_total.labels(action="run").inc()
    return ok({"result": result.model_dump(mode="json")})


@router.post("/jobs/{job_id}/pause")
def pause_job(job_id: str) -> dict:
    try:
        job = _service().pause_job(job_id)
    except JobNotFoundError as exc:
        return fail("SCHEDULER_JOB_NOT_FOUND", str(exc))
    except Exception as exc:
        return fail("SCHEDULER_JOB_PAUSE_FAILED", str(exc))
    scheduler_job_total.labels(action="pause").inc()
    return ok({"job": job.model_dump(mode="json")})


@router.post("/jobs/{job_id}/resume")
def resume_job(job_id: str) -> dict:
    try:
        job = _service().resume_job(job_id)
    except JobNotFoundError as exc:
        return fail("SCHEDULER_JOB_NOT_FOUND", str(exc))
    except Exception as exc:
        return fail("SCHEDULER_JOB_RESUME_FAILED", str(exc))
    scheduler_job_total.labels(action="resume").inc()
    return ok({"job": job.model_dump(mode="json")})


@router.delete("/jobs/{job_id}")
def delete_job(job_id: str) -> dict:
    deleted = _service().delete_job(job_id)
    if not deleted:
        return fail("SCHEDULER_JOB_NOT_FOUND", f"Unknown job: {job_id}")
    scheduler_job_total.labels(action="delete").inc()
    return ok({"deleted": True, "job_id": job_id})


@router.get("/runs")
def list_runs() -> dict:
    runs = [run.model_dump(mode="json") for run in _service().list_runs()]
    return ok({"runs": runs})


@router.get("/runs/{job_id}")
def list_runs_for_job(job_id: str) -> dict:
    runs = [run.model_dump(mode="json") for run in _service().list_runs(job_id=job_id)]
    return ok({"runs": runs, "job_id": job_id})
