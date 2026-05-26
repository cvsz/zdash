from pydantic import BaseModel

class StrategicThesis(BaseModel):
    thesis: str
    confidence: float
    horizon_years: int
