from fastapi import APIRouter
from app.core.responses import ok
from app.notifications.notification_service import EVENTS,send_notification
router=APIRouter(prefix="/api/notifications",tags=["notifications"])
@router.get("/status")
def status(): return ok({"dry_run":True,"count":len(EVENTS)})
@router.post("/test")
def test(): return ok(send_notification("test","dry",{},True))
