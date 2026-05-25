from pydantic import BaseModel
from typing import Literal,Any

TaskStatus=Literal["queued","running","completed","failed","retrying","cancelled"]

class WorkerTask(BaseModel):
    id:str
    organization_id:str
    workspace_id:str
    task_type:str
    status:TaskStatus="queued"
    payload:dict[str,Any]={}
    result:dict[str,Any]|None=None
    error:str|None=None
    priority:int=5
    attempts:int=0
    max_retries:int=3
