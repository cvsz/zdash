from .models import TwinEntity
class EntityRegistry:
    def __init__(self): self._items:dict[str,TwinEntity]={}
    def create_entity(self,e:TwinEntity)->TwinEntity: self._items[e.id]=e; return e
    def list_entities(self,org:str,ws:str): return [v for v in self._items.values() if v.organization_id==org and v.workspace_id==ws]
    def get_entity(self,org:str,ws:str,eid:str):
        e=self._items.get(eid); return e if e and e.organization_id==org and e.workspace_id==ws else None
    def update_entity(self,org:str,ws:str,eid:str,patch:dict):
        e=self.get_entity(org,ws,eid)
        if not e: return None
        for k,v in patch.items():
            if hasattr(e,k): setattr(e,k,v)
        return e
    def archive_entity(self,org:str,ws:str,eid:str)->bool:
        return self._items.pop(eid,None) is not None
