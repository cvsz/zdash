from pydantic import BaseModel

class AlertRule(BaseModel):
    id:str; organization_id:str; workspace_id:str; name:str; event_type:str; severity:str="warning"; enabled:bool=True; condition:str="true"; channels:list[str]=[]
