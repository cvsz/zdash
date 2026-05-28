from __future__ import annotations

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api import workspaces as workspaces_api
from app.api.workspaces import FederationRegisterRequest
from app.auth.models import AuthSession
from app.auth.rbac import Permission


@pytest.fixture(autouse=True)
def reset_peers() -> None:
    workspaces_api._peers.clear()


def _dependency_calls(path: str, method: str) -> list[object]:
    for route in workspaces_api.router.routes:
        methods = getattr(route, "methods", set())
        if getattr(route, "path", "") == f"/api/workspaces/federation{path}" and method in methods:
            return [dependency.call for dependency in route.dependant.dependencies]
    raise AssertionError(f"route not found: {method} {path}")


def _has_permission_dependency(calls: list[object], permission: Permission) -> bool:
    for call in calls:
        closure = getattr(call, "__closure__", None) or ()
        if any(getattr(cell, "cell_contents", None) == permission for cell in closure):
            return True
    return False


def _permission_dependency(path: str, method: str, permission: Permission):
    for call in _dependency_calls(path, method):
        closure = getattr(call, "__closure__", None) or ()
        if any(getattr(cell, "cell_contents", None) == permission for cell in closure):
            return call
    raise AssertionError(f"permission dependency not found: {method} {path} {permission}")


def test_federation_status_is_public() -> None:
    assert _dependency_calls("/status", "GET") == []


def test_federation_peers_and_register_require_tenancy_permissions() -> None:
    peer_dependencies = _dependency_calls("/peers", "GET")
    register_dependencies = _dependency_calls("/register", "POST")
    assert _has_permission_dependency(peer_dependencies, Permission.READ_TENANCY)
    assert _has_permission_dependency(register_dependencies, Permission.MANAGE_TENANCY)


def test_register_permission_dependency_denies_viewer_role() -> None:
    dependency = _permission_dependency("/register", "POST", Permission.MANAGE_TENANCY)
    with pytest.raises(HTTPException) as exc_info:
        dependency(AuthSession(username="viewer-user", role="viewer"))
    assert exc_info.value.status_code == 403


def test_register_uses_typed_payload_and_persists_peer() -> None:
    admin = AuthSession(username="admin", role="admin")
    payload = FederationRegisterRequest(name="edge-alpha")
    register_response = workspaces_api.register(payload, _=admin)
    assert register_response["ok"] is True
    assert register_response["data"]["item"]["name"] == "edge-alpha"

    peers_response = workspaces_api.peers(_=admin)
    assert peers_response["ok"] is True
    assert peers_response["data"]["items"][0]["name"] == "edge-alpha"


def test_register_name_rejects_length_over_limit() -> None:
    with pytest.raises(ValidationError):
        FederationRegisterRequest(name="x" * 65)
