from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.responses import ok

router = APIRouter(tags=['health'])


@router.get('/health')
def health() -> dict:
    settings = get_settings()
    return ok(
        {
            'app_name': settings.app_name,
            'environment': settings.app_env,
            'status': 'ok',
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
    )
