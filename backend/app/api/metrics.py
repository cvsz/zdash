from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from app.observability.metrics import render_metrics

router = APIRouter(prefix="/api", tags=["metrics"])


@router.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return render_metrics()
