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
    READ_TENANCY = "read_tenancy"
    MANAGE_TENANCY = "manage_tenancy"
    READ_WORKERS = "read_workers"
    MANAGE_WORKERS = "manage_workers"
    READ_NOTIFICATIONS = "read_notifications"
    MANAGE_NOTIFICATIONS = "manage_notifications"

    # Phase 10 Billing
    billing_read = "billing.read"
    billing_manage = "billing.manage"
    billing_apply_mock_plan = "billing.apply_mock_plan"
    
    # Phase 10 Usage
    usage_read = "usage.read"
    
    # Phase 10 Marketplace
    marketplace_read = "marketplace.read"
    marketplace_install = "marketplace.install"
    marketplace_manage = "marketplace.manage"
    marketplace_run_plugin = "marketplace.run_plugin"
    
    # Phase 10 Enterprise
    enterprise_read = "enterprise.read"
    enterprise_license_manage = "enterprise.license.manage"
    enterprise_branding_manage = "enterprise.branding.manage"
    enterprise_export = "enterprise.export"
    enterprise_export_secrets = "enterprise.export_secrets"
    enterprise_onboarding_manage = "enterprise.onboarding.manage"


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
        Permission.READ_TENANCY.value,
        Permission.MANAGE_TENANCY.value,
        Permission.READ_WORKERS.value,
        Permission.MANAGE_WORKERS.value,
        Permission.READ_NOTIFICATIONS.value,
        Permission.MANAGE_NOTIFICATIONS.value,
        Permission.billing_read.value,
        Permission.usage_read.value,
        Permission.marketplace_read.value,
        Permission.marketplace_install.value,
        Permission.marketplace_run_plugin.value,
        Permission.enterprise_read.value,
        Permission.enterprise_branding_manage.value,
        Permission.enterprise_onboarding_manage.value,
    },
    RoleName.analyst.value: {
        Permission.READ_DASHBOARD.value,
        Permission.RUN_BACKTESTS.value,
        Permission.READ_LOGS.value,
        Permission.READ_RISK.value,
        Permission.READ_TRADING_SIGNALS.value,
        Permission.READ_TENANCY.value,
        Permission.READ_WORKERS.value,
        Permission.READ_NOTIFICATIONS.value,
        Permission.billing_read.value,
        Permission.usage_read.value,
        Permission.marketplace_read.value,
        Permission.enterprise_read.value,
    },
    RoleName.viewer.value: {
        Permission.READ_DASHBOARD.value,
        Permission.READ_TENANCY.value,
        Permission.READ_WORKERS.value,
        Permission.READ_NOTIFICATIONS.value,
        Permission.billing_read.value,
        Permission.usage_read.value,
        Permission.marketplace_read.value,
        Permission.enterprise_read.value,
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
