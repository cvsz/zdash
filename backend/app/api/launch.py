from fastapi import APIRouter

from app.core.responses import ok
from app.launch.docs_publish_service import DocsPublishService
from app.launch.invite_service import InviteService
from app.launch.launch_readiness import LaunchReadinessService
from app.launch.public_status_service import PublicStatusService
from app.launch.release_notes import ReleaseNotesService
from app.launch.telemetry_service import TelemetryService
from app.launch.waitlist_service import WaitlistService

router = APIRouter(prefix='/api/launch', tags=['launch'])
waitlist = WaitlistService()
invites = InviteService()
status_service = PublicStatusService()
readiness = LaunchReadinessService()
notes = ReleaseNotesService()
telemetry = TelemetryService()
docs = DocsPublishService()


@router.get('/public/status')
def public_status():
    return ok(status_service.get_public_status_summary())


@router.post('/waitlist/join')
def waitlist_join(request: dict):
    return ok({'entry': waitlist.join_waitlist(request).model_dump(mode='json', exclude={'email'})})


@router.post('/invites/validate')
def invite_validate(request: dict):
    return ok({'valid': bool(request.get('code'))})


@router.get('/readiness')
def get_readiness():
    return ok(readiness.run_all_checks())


@router.post('/release-notes/generate')
def generate_release_notes(request: dict):
    return ok(notes.generate_release_notes(request.get('from_version', '0.0.0'), request.get('to_version', '0.0.0')))


@router.post('/docs/publish')
def publish_docs(request: dict):
    return ok(docs.publish_docs(bool(request.get('dry_run', True))))


@router.post('/telemetry')
def record_telemetry(request: dict):
    return ok({'payload': telemetry.redact_payload(request.get('payload', {}))})
