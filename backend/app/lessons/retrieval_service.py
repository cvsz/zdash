from .lessons_service import lessons_feed


def retrieve_lessons() -> dict:
    return {"lessons": [l.model_dump() for l in lessons_feed()]}
