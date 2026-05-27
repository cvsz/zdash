from app.realtime.broadcaster import get_realtime_broadcaster
from app.realtime.models import RealtimeEvent
from app.realtime.schemas import RealtimeEventEnvelope


async def publish_event(event: RealtimeEvent) -> dict:
    envelope = RealtimeEventEnvelope(
        id=event.event_id,
        type=event.type,
        source=event.source,
        severity=event.severity,
        payload=event.payload,
        data=event.payload,
    )
    return await get_realtime_broadcaster().apublish(envelope)
