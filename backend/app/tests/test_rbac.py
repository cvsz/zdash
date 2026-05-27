from app.auth.rbac import Permission, has_permission


def test_admin_has_all_permissions() -> None:
    for permission in Permission:
        assert has_permission("admin", permission) is True


def test_operator_permissions() -> None:
    assert has_permission("operator", Permission.READ_DASHBOARD) is True
    assert has_permission("operator", Permission.MANAGE_SCHEDULER) is True
    assert has_permission("operator", Permission.READ_LOGS) is False


def test_analyst_permissions() -> None:
    assert has_permission("analyst", Permission.READ_DASHBOARD) is True
    assert has_permission("analyst", Permission.RUN_BACKTESTS) is True
    assert has_permission("analyst", Permission.READ_LOGS) is True
    assert has_permission("analyst", Permission.MANAGE_CONTENT_APPROVAL) is False


def test_viewer_permissions() -> None:
    assert has_permission("viewer", Permission.READ_DASHBOARD) is True
    assert has_permission("viewer", Permission.RUN_BACKTESTS) is False
