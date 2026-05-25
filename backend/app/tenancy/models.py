from pydantic import BaseModel
from typing import Literal

Status=Literal["active","suspended","archived"]
WorkspaceEnv=Literal["development","staging","production","simulation"]

class OrganizationIn(BaseModel):
    name:str
    slug:str

class WorkspaceIn(BaseModel):
    name:str
    slug:str
    environment:WorkspaceEnv="development"
