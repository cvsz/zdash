from types import SimpleNamespace

from app.auth.models import AuthSession
from app.tenancy.dependencies import get_tenant_context


def test_context_defaults():
    tc = get_tenant_context(
        SimpleNamespace(headers={}),
        AuthSession(username="dev-user", role="admin"),
    )
    assert tc.organization_id
