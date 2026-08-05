from fastapi import APIRouter, Depends

from app.auth.dependencies import require_authenticated
from app.core.responses import ok
from app.marketing.service import MarketingDashboardService

router = APIRouter(prefix="/api/marketing", tags=["marketing"])


@router.get("/overview")
def overview(_: object = Depends(require_authenticated)):
    dashboard = MarketingDashboardService().build()
    return ok(dashboard.model_dump(mode="json"))
