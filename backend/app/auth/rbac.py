from enum import Enum
from fastapi import HTTPException


class Role(str, Enum):
    admin = "admin"
    operator = "operator"
    analyst = "analyst"
    viewer = "viewer"


class Permission(str, Enum):
    READ_DASHBOARD = "read_dashboard"
    MANAGE_USERS = "manage_users"
    HALT_RISK = "halt_risk"


ROLE_PERMISSIONS = {
    Role.admin: {p for p in Permission},
    Role.operator: {Permission.READ_DASHBOARD, Permission.HALT_RISK},
    Role.analyst: {Permission.READ_DASHBOARD},
    Role.viewer: {Permission.READ_DASHBOARD},
}


def require_permission(permission: Permission, role: str):
    if permission not in ROLE_PERMISSIONS.get(Role(role), set()):
        raise HTTPException(status_code=403, detail="Insufficient permissions")


def require_role(role: Role, current_role: str):
    if current_role != role.value:
        raise HTTPException(status_code=403, detail="Insufficient role")
