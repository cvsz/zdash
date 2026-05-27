import asyncio

import pytest
from fastapi import HTTPException

from app.api.routes.incidents import (
    ack_incident,
    create_incident,
    list_incidents,
    resolve_incident,
)
from app.auth.models import AuthSession
from app.services.incidents import reset_incident_service as reset_incident_service_state


@pytest.fixture(autouse=True)
def reset_incident_service_fixture() -> None:
    reset_incident_service_state()
    yield
    reset_incident_service_state()


def test_incident_rbac_flow() -> None:
    viewer = AuthSession(username="viewer_u", role="viewer")
    operator = AuthSession(username="op_u", role="operator")
    admin = AuthSession(username="admin_u2", role="admin")

    list_response = asyncio.run(list_incidents(user=viewer))
    assert list_response["ok"] is True

    with pytest.raises(HTTPException) as viewer_create_error:
        asyncio.run(create_incident({"title": "x", "severity": "warning"}, user=viewer))
    assert viewer_create_error.value.status_code == 403

    created_response = asyncio.run(
        create_incident({"title": "x", "severity": "warning"}, user=operator)
    )
    incident_id = created_response["data"]["id"]

    ack_response = asyncio.run(ack_incident(incident_id, user=operator))
    assert ack_response["ok"] is True
    assert ack_response["data"]["status"] == "acknowledged"

    with pytest.raises(HTTPException) as operator_resolve_error:
        asyncio.run(resolve_incident(incident_id, {"notes": "done"}, user=operator))
    assert operator_resolve_error.value.status_code == 403

    resolved_response = asyncio.run(
        resolve_incident(incident_id, {"notes": "done"}, user=admin)
    )
    assert resolved_response["ok"] is True
    assert resolved_response["data"]["status"] == "resolved"
