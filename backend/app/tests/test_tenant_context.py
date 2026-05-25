from app.tenancy.dependencies import get_tenant_context

def test_context_defaults():
    tc=get_tenant_context(None,None)
    assert tc.organization_id
