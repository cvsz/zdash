from .models import TwinRelationship


class RelationshipService:
    def __init__(self):
        self._items: dict[str, TwinRelationship] = {}

    def validate_relationship(self, r: TwinRelationship) -> bool:
        return r.source_entity_id != r.target_entity_id

    def create_relationship(self, r: TwinRelationship):
        if not self.validate_relationship(r):
            raise ValueError("invalid relationship")
        self._items[r.id] = r
        return r

    def list_relationships(self, org: str, ws: str):
        return [
            v
            for v in self._items.values()
            if v.organization_id == org and v.workspace_id == ws
        ]

    def get_relationship(self, org: str, ws: str, rid: str):
        r = self._items.get(rid)
        return r if r and r.organization_id == org and r.workspace_id == ws else None

    def delete_relationship(self, org: str, ws: str, rid: str) -> bool:
        r = self.get_relationship(org, ws, rid)
        if not r:
            return False
        del self._items[rid]
        return True
