from app.developer.models import ApiKeyScope, ApiKeyStatus


def test_api_key_status_enum():
    assert ApiKeyStatus.ACTIVE == "active"


def test_scope_enum():
    assert ApiKeyScope.READ_RISK == "read:risk"
