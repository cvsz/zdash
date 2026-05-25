from __future__ import annotations
from uuid import uuid4
from datetime import datetime
from .models import Incident, IncidentStatus

class IncidentService:
    def __init__(self): self._items:dict[str,Incident]={}
    def create_incident(self, request:dict)->Incident:
        i=Incident(id=str(uuid4()), **request); self._items[i.id]=i; return i
    def list_incidents(self, filters:dict|None=None)->list[Incident]: return list(self._items.values())
    def get_incident(self, incident_id:str)->Incident: return self._items[incident_id]
    def acknowledge_incident(self, incident_id:str, user_id:str)->Incident:
        i=self._items[incident_id]; i.status=IncidentStatus.acknowledged; i.acknowledged_at=datetime.utcnow(); i.assigned_to=user_id; return i
    def update_incident_status(self, incident_id:str, status, notes:str='')->Incident:
        i=self._items[incident_id]; i.status=status; i.metadata['notes']=notes; i.updated_at=datetime.utcnow(); return i
    def resolve_incident(self, incident_id:str, notes:str='')->Incident:
        i=self._items[incident_id]; i.status=IncidentStatus.resolved; i.resolved_at=datetime.utcnow(); i.metadata['resolution_notes']=notes; return i
    def link_remediation(self, incident_id:str, remediation_id:str): self._items[incident_id].metadata.setdefault('remediations',[]).append(remediation_id)
