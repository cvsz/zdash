from fastapi import APIRouter
from app.core.responses import ok
from app.lessons.retrieval_service import retrieve_lessons

router = APIRouter(prefix="/api/lessons", tags=["lessons"])


@router.get("/memory")
def memory():
    return ok(retrieve_lessons())
