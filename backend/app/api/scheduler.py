from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.audit.audit_service import AuditService
from app.audit.models import AuditLogCreate
from app.auth.dependencies import require_authenticated, require_permission
from app.auth.models import AuthSession
from app.auth.rbac import Permission
from app.billing.entitlement_service import require_feature
from app.billing.quota_service import consume
from app.core.observability import scheduler_job_total
from app.core.responses import fail, ok
from app.db.session import get_db_session
from app.observability.metrics import metrics_store
from app.scheduler import CreateJobRequest
from app.scheduler.job_store import JobNotFoundError
from app.scheduler.scheduler_service import get_scheduler_service
from app.tenancy.dependencies import get_tenant_context
from app.tenancy.tenant_context import TenantContext

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


def _service():
    return get_scheduler_service()


def _actor_email(current_user: object) -> str:
    if isinstance(current_user, AuthSession):
        return current_user.username
    return "system"


def _maybe_audit(session: object, entry: AuditLogCreate) -> None:
    if isinstance(session, Session):
        AuditService(session).log(entry)


@router.get("/status")
def status(_: object = Depends(require_authenticated)) -> dict:
    return ok({"scheduler": _service().get_status()})


@router.get("/jobs")
def list_jobs(_: object = Depends(require_authenticated)) -> dict:
    jobs = [job.model_dump(mode="json") for job in _service().list_jobs()]
    return ok({"jobs": jobs})


@router.post("/jobs")
def create_job(
    req: CreateJobRequest,
    current_user: AuthSession = Depends(require_permission(Permission.MANAGE_SCHEDULER)),
    session: Session = Depends(get_db_session),
    _f: str = Depends(require_feature("feature.scheduler")),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict:
    try:
        org_id = getattr(tenant, "organization_id", "default")
        ws_id = getattr(tenant, "workspace_id", "default")
        decision = consume(org_id, ws_id, "scheduler_jobs")
        if not decision.allowed:
            return fail("QUOTA_EXCEEDED", "Scheduler jobs quota exceeded")
            
        job = _service().create_job(req)
    except ValueError as exc:
        return fail("SCHEDULER_JOB_INVALID", str(exc))
    scheduler_job_total.labels(action="create").inc()
    metrics_store.increment_scheduler_jobs()
    _maybe_audit(
        session,
        AuditLogCreate(
            actor_user_id="",
            actor_email=_actor_email(current_user),
            action="scheduler.job.create",
            resource_type="scheduler_job",
            resource_id=job.id,
            metadata={"name": job.name, "job_type": job.job_type},
        ),
    )
    return ok({"job": job.model_dump(mode="json")})


@router.post("/jobs/{job_id}/run")
def run_job(
    job_id: str,
    current_user: AuthSession = Depends(require_permission(Permission.MANAGE_SCHEDULER)),
    session: Session = Depends(get_db_session),
) -> dict:
    try:
        result = _service().run_job(job_id, manual=True)
    except JobNotFoundError as exc:
        return fail("SCHEDULER_JOB_NOT_FOUND", str(exc))
    except Exception as exc:
        return fail("SCHEDULER_JOB_RUN_FAILED", str(exc))
    scheduler_job_total.labels(action="run").inc()
    metrics_store.increment_scheduler_jobs()
    _maybe_audit(
        session,
        AuditLogCreate(
            actor_user_id="",
            actor_email=_actor_email(current_user),
            action="scheduler.job.run",
            resource_type="scheduler_job",
            resource_id=job_id,
            metadata={"status": result.status},
        ),
    )
    return ok({"result": result.model_dump(mode="json")})


@router.post("/jobs/{job_id}/pause")
def pause_job(
    job_id: str,
    _: object = Depends(require_permission(Permission.MANAGE_SCHEDULER)),
) -> dict:
    try:
        job = _service().pause_job(job_id)
    except JobNotFoundError as exc:
        return fail("SCHEDULER_JOB_NOT_FOUND", str(exc))
    except Exception as exc:
        return fail("SCHEDULER_JOB_PAUSE_FAILED", str(exc))
    scheduler_job_total.labels(action="pause").inc()
    return ok({"job": job.model_dump(mode="json")})


@router.post("/jobs/{job_id}/resume")
def resume_job(
    job_id: str,
    _: object = Depends(require_permission(Permission.MANAGE_SCHEDULER)),
) -> dict:
    try:
        job = _service().resume_job(job_id)
    except JobNotFoundError as exc:
        return fail("SCHEDULER_JOB_NOT_FOUND", str(exc))
    except Exception as exc:
        return fail("SCHEDULER_JOB_RESUME_FAILED", str(exc))
    scheduler_job_total.labels(action="resume").inc()
    return ok({"job": job.model_dump(mode="json")})


@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: str,
    current_user: AuthSession = Depends(require_permission(Permission.MANAGE_SCHEDULER)),
    session: Session = Depends(get_db_session),
) -> dict:
    deleted = _service().delete_job(job_id)
    if not deleted:
        return fail("SCHEDULER_JOB_NOT_FOUND", f"Unknown job: {job_id}")
    scheduler_job_total.labels(action="delete").inc()
    metrics_store.increment_scheduler_jobs()
    _maybe_audit(
        session,
        AuditLogCreate(
            actor_user_id="",
            actor_email=_actor_email(current_user),
            action="scheduler.job.delete",
            resource_type="scheduler_job",
            resource_id=job_id,
            metadata={"deleted": True},
        ),
    )
    return ok({"deleted": True, "job_id": job_id})


@router.get("/runs")
def list_runs(_: object = Depends(require_authenticated)) -> dict:
    runs = [run.model_dump(mode="json") for run in _service().list_runs()]
    return ok({"runs": runs})


@router.get("/runs/{job_id}")
def list_runs_for_job(
    job_id: str,
    _: object = Depends(require_authenticated),
) -> dict:
    runs = [run.model_dump(mode="json") for run in _service().list_runs(job_id=job_id)]
    return ok({"runs": runs, "job_id": job_id})
