from .tenant_context import TenantContext
from . import repositories as r

class TenantService:
    def list_orgs(self,user_id:str,admin:bool=False):
        if admin: return list(r.TENANTS.values())
        allowed={m["organization_id"] for m in r.MEMBERS.values() if m["user_id"]==user_id}
        return [o for o in r.TENANTS.values() if o["id"] in allowed]

service=TenantService()
