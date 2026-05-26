from .models import Lesson

def lessons_feed() -> list[Lesson]:
    return [Lesson(source="postmortem", learning="Require rollback plans in all proposals")]
