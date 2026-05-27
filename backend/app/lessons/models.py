from pydantic import BaseModel


class Lesson(BaseModel):
    source: str
    learning: str
