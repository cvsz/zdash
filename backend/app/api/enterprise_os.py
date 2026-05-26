from fastapi import APIRouter
from app.core.responses import ok
from app.enterprise_os.enterprise_os_report_service import enterprise_os_report

router = APIRouter(prefix="/api/enterprise-os", tags=["enterprise-os"])

@router.get("/report")
def report():
    return ok(enterprise_os_report())
