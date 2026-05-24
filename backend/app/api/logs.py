from fastapi import APIRouter, Query

from app.core.events import event_bus
from app.core.responses import ok

router = APIRouter(prefix='/api/logs', tags=['logs'])


@router.get('')
def list_logs(limit: int = Query(default=100, ge=1, le=1000)) -> dict:
    events = [event.model_dump() for event in event_bus.list_events(limit=limit)]
    return ok({'events': events})
