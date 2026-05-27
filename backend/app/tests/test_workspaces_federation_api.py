from __future__ import annotations

import pytest

from app.api import workspaces as workspaces_api
from app.api.workspaces import FederationRegisterRequest
from app.auth.dependencies import require_authenticated
from app.auth.models import AuthSession


@pytest.fixture(autouse=True)
def reset_peers() -> None:
    workspaces_api._peers.clear()


def _dependency_calls(path: str, method: str) -> list[object]:
    for route in workspaces_api.router.routes:
        methods = getattr(route, "methods", set())
        if getattr(route, "path", "") == f"/api/workspaces/federation{path}" and method in methods:
            return [dependency.call for dependency in route.dependant.dependencies]
    raise AssertionError(f"route not found: {method} {path}")


def test_federation_status_is_public() -> None:
    assert _dependency_calls("/status", "GET") == []


def test_federation_peers_and_register_require_auth_dependency() -> None:
    peer_dependencies = _dependency_calls("/peers", "GET")
    register_dependencies = _dependency_calls("/register", "POST")
    assert require_authenticated in peer_dependencies
    assert require_authenticated in register_dependencies


def test_register_uses_typed_payload_and_persists_peer() -> None:
    admin = AuthSession(username="admin", role="admin")
    payload = FederationRegisterRequest(name="edge-alpha")
    register_response = workspaces_api.register(payload, _=admin)
    assert register_response["ok"] is True
    assert register_response["data"]["item"]["name"] == "edge-alpha"

    peers_response = workspaces_api.peers(_=admin)
    assert peers_response["ok"] is True
    assert peers_response["data"]["items"][0]["name"] == "edge-alpha"
