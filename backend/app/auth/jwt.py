from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import get_settings


def create_access_token(sub: str, role: str) -> str:
    s = get_settings()
    exp = datetime.now(timezone.utc) + timedelta(
        minutes=s.jwt_access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": sub, "role": role, "exp": exp},
        s.jwt_secret_key,
        algorithm=s.jwt_algorithm,
    )
