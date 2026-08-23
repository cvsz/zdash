import pytest
from fastapi import HTTPException

from app.auth.jwt import create_access_token as create_typed_access_token
from app.auth.jwt import create_refresh_token, decode_token
from app.core.auth import create_access_token, decode_access_token


def test_core_access_token_round_trip_preserves_identity_and_role() -> None:
    token = create_access_token("alice", "admin")

    decoded = decode_access_token(token)

    assert decoded.username == "alice"
    assert decoded.role == "admin"


def test_typed_access_and_refresh_tokens_preserve_token_type() -> None:
    access = decode_token(create_typed_access_token("alice", "operator"))
    refresh = decode_token(create_refresh_token("alice", "operator"))

    assert access["sub"] == "alice"
    assert access["role"] == "operator"
    assert access["type"] == "access"
    assert refresh["sub"] == "alice"
    assert refresh["role"] == "operator"
    assert refresh["type"] == "refresh"
    assert refresh["jti"]


def test_invalid_tokens_fail_closed() -> None:
    with pytest.raises(ValueError, match="Invalid token"):
        decode_token("not-a-jwt")

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token("not-a-jwt")

    assert exc_info.value.status_code == 401
