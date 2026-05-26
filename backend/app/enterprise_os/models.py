from pydantic import BaseModel

class Capability(BaseModel):
    name: str
    maturity: int
    owner: str
