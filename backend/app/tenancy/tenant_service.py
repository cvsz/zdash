from . import repositories as r


class TenantService:
    def list_orgs(self, user_id: str, admin: bool = False):
        if admin:
            return list(r.TENANTS.values())
        allowed = {
            member["organization_id"]
            for members in r.MEMBERS.values()
            for member in members
            if member.get("user_id") == user_id
        }
        return [o for o in r.TENANTS.values() if o["id"] in allowed]


service = TenantService()
