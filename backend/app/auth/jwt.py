from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt

from app.core.config import get_settings


def create_access_token(sub: str, role: str) -> str:
    s = get_settings()
    exp = datetime.now(timezone.utc) + timedelta(
        minutes=s.jwt_access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": sub, "role": role, "exp": exp, "type": "access"},
        s.jwt_secret_key,
        algorithm=s.jwt_algorithm,
    )


def create_refresh_token(sub: str, role: str) -> str:
    s = get_settings()
    exp = datetime.now(timezone.utc) + timedelta(days=s.jwt_refresh_token_expire_days)
    return jwt.encode(
        {"sub": sub, "role": role, "exp": exp, "type": "refresh", "jti": str(uuid4())},
        s.jwt_secret_key,
        algorithm=s.jwt_algorithm,
    )


def decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
