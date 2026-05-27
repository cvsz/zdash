from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any


class BoardRole(str, Enum):
    ceo = "ceo"
    coo = "coo"
    cfo = "cfo"
    cto = "cto"
    ciso = "ciso"
    cro = "cro"
    cmo = "cmo"
    general_counsel = "general_counsel"
    investor_advisor = "investor_advisor"
    customer_advocate = "customer_advocate"


class BoardDecisionStatus(str, Enum):
    draft = "draft"
    debated = "debated"
    voted = "voted"
    approved = "approved"
    rejected = "rejected"
    deferred = "deferred"
    archived = "archived"


class BoardVoteValue(str, Enum):
    approve = "approve"
    reject = "reject"
    abstain = "abstain"
    request_more_info = "request_more_info"


class BoardAgent(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    role: BoardRole
    name: str
    mandate: str
    risk_focus: str
    decision_weight: float = 1.0
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BoardDebateSession(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    topic: str
    prompt: str
    status: BoardDecisionStatus = BoardDecisionStatus.draft
    participants: list[BoardRole] = []
    transcript: list[dict[str, Any]] = []
    assumptions: list[str] = []
    risks: list[str] = []
    recommendations: list[dict[str, Any]] = []
    confidence: float = 0.6
    limitations: list[str] = ["Advisory only"]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class BoardVote(BaseModel):
    id: str
    session_id: str
    agent_role: BoardRole
    vote: BoardVoteValue
    rationale: str
    confidence: float = 0.6
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BoardDecision(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    title: str
    summary: str
    status: BoardDecisionStatus = BoardDecisionStatus.draft
    decision_type: str = "advisory"
    recommended_action: str
    owner: str
    due_date: datetime | None = None
    risks: list[str] = []
    assumptions: list[str] = []
    evidence: list[str] = []
    votes: list[BoardVote] = []
    limitations: list[str] = ["No automatic execution"]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BoardMeeting(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    title: str
    agenda: list[str] = []
    minutes: str = ""
    decisions: list[str] = []
    action_items: list[str] = []
    created_by: str
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DecisionMemo(BaseModel):
    id: str
    organization_id: str
    workspace_id: str
    title: str
    decision_question: str
    context: str
    options: list[str]
    recommendation: str
    risks: list[str]
    assumptions: list[str]
    evidence: list[str]
    dissenting_views: list[str] = []
    confidence: float = 0.6
    limitations: list[str] = ["Operational template only"]
    status: BoardDecisionStatus = BoardDecisionStatus.draft
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
