from pydantic import BaseModel


class AuditEntry(BaseModel):
    action: str
    actor_email: str
