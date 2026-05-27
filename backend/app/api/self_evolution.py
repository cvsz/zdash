from fastapi import APIRouter
from app.core.responses import ok
from app.self_evolution.evolution_review_queue import review_queue

router = APIRouter(prefix="/api/self-evolution", tags=["self-evolution"])


@router.get("/queue")
def queue():
    return ok(review_queue())
