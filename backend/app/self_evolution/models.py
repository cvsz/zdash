from pydantic import BaseModel


class ImprovementProposal(BaseModel):
    id: str
    title: str
    confidence: float
    requires_human_approval: bool = True
