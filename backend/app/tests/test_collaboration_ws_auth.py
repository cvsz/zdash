from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

from app.auth.jwt import create_access_token
from app.core.config import get_settings

collaboration_router = importlib.import_module("app.collaboration.router")


def _fake_websocket(
    *,
    query_token: str | None = None,
    subprotocol_header: str | None = None,
) -> SimpleNamespace:
    query_params = {}
    headers = {}
    if query_token is not None:
        query_params["token"] = query_token
    if subprotocol_header is not None:
        headers["sec-websocket-protocol"] = subprotocol_header
    return SimpleNamespace(query_params=query_params, headers=headers)


def test_extract_token_from_query_string() -> None:
    websocket = _fake_websocket(query_token="query-token")
    assert collaboration_router._extract_websocket_token(websocket) == "query-token"


def test_extract_token_from_subprotocol_header() -> None:
    websocket = _fake_websocket(subprotocol_header="bearer, subprotocol-token")
    assert collaboration_router._extract_websocket_token(websocket) == "subprotocol-token"


def test_authenticate_websocket_requires_token_when_auth_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AUTH_ENABLED", "true")
    get_settings.cache_clear()
    websocket = _fake_websocket()
    assert collaboration_router._authenticate_websocket(websocket) is None


def test_authenticate_websocket_accepts_valid_access_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AUTH_ENABLED", "true")
    get_settings.cache_clear()
    token = create_access_token("alice", "operator")
    websocket = _fake_websocket(subprotocol_header=f"bearer, {token}")
    user = collaboration_router._authenticate_websocket(websocket)
    assert user is not None
    assert user.username == "alice"
    assert user.role == "operator"


def test_authenticate_websocket_allows_dev_mode_when_auth_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AUTH_ENABLED", "false")
    get_settings.cache_clear()
    websocket = _fake_websocket()
    user = collaboration_router._authenticate_websocket(websocket)
    assert user is not None
    assert user.username == "dev-user"
    assert user.role == "admin"
