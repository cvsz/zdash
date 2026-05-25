from pydantic import BaseModel

class AuthUser(BaseModel):
    id: str
    email: str
    role: str
