from __future__ import annotations

from enum import Enum


class RoleName(str, Enum):
    admin = "admin"
    operator = "operator"
    analyst = "analyst"
    viewer = "viewer"


class Permission(str, Enum):
    READ_DASHBOARD = "read_dashboard"
    RUN_DRY_RUN_TRADING = "run_dry_run_trading"
    MANAGE_SCHEDULER = "manage_scheduler"
    MANAGE_CONTENT_APPROVAL = "manage_content_approval"
    RUN_BACKTESTS = "run_backtests"
    CONTROL_DRY_RUN_IOT = "control_dry_run_iot"
    HALT_RESUME_RISK = "halt_resume_risk"
    READ_LOGS = "read_logs"
    READ_RISK = "read_risk"
    READ_TRADING_SIGNALS = "read_trading_signals"


ROLE_PERMISSIONS = {
    RoleName.admin.value: {permission.value for permission in Permission},
    RoleName.operator.value: {
        Permission.READ_DASHBOARD.value,
        Permission.RUN_DRY_RUN_TRADING.value,
        Permission.MANAGE_SCHEDULER.value,
        Permission.MANAGE_CONTENT_APPROVAL.value,
        Permission.RUN_BACKTESTS.value,
        Permission.CONTROL_DRY_RUN_IOT.value,
        Permission.HALT_RESUME_RISK.value,
        Permission.READ_RISK.value,
        Permission.READ_TRADING_SIGNALS.value,
    },
    RoleName.analyst.value: {
        Permission.READ_DASHBOARD.value,
        Permission.RUN_BACKTESTS.value,
        Permission.READ_LOGS.value,
        Permission.READ_RISK.value,
        Permission.READ_TRADING_SIGNALS.value,
    },
    RoleName.viewer.value: {
        Permission.READ_DASHBOARD.value,
    },
}


def normalize_role(role: str) -> str:
    if role not in ROLE_PERMISSIONS:
        return RoleName.viewer.value
    return role


def has_permission(role: str, permission: str | Permission) -> bool:
    normalized_role = normalize_role(role)
    permission_value = (
        permission.value if isinstance(permission, Permission) else str(permission)
    )
    if normalized_role == RoleName.admin.value:
        return True
    return permission_value in ROLE_PERMISSIONS.get(normalized_role, set())
