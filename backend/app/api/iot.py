from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, require_roles
from app.core.responses import ok
from app.iot.iot_service import IoTService
from app.iot.models import IoTActionRequest

router = APIRouter(prefix='/api/iot', tags=['iot'])
service = IoTService()


@router.post('/power-cycle')
def power_cycle(req: IoTActionRequest, current_user: CurrentUser = Depends(require_roles('admin', 'operator'))):
    return ok({'result': service.power_cycle(confirmation=req.confirmation)})
