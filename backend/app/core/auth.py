from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session

from app.core.config import get_settings
from app.core.database import get_session
from app.repositories import Repository

pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')


class TokenData(BaseModel):
    username: str
    role: str


class CurrentUser(BaseModel):
    username: str
    role: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(username: str, role: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {'sub': username, 'role': role, 'exp': expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> TokenData:
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username = payload.get('sub')
        role = payload.get('role')
        if username is None or role is None:
            raise credentials_exception
        return TokenData(username=username, role=role)
    except JWTError as exc:
        raise credentials_exception from exc


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> CurrentUser:
    td = decode_access_token(token)
    return CurrentUser(username=td.username, role=td.role)


def require_roles(*roles: str):
    def _dependency(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail='Insufficient role')
        return user

    return _dependency


def bootstrap_admin(session: Session) -> None:
    settings = get_settings()
    repo = Repository(session)
    existing = repo.get_user_by_username(settings.bootstrap_admin_username)
    if existing is None:
        repo.add_user(
            username=settings.bootstrap_admin_username,
            password_hash=get_password_hash(settings.bootstrap_admin_password),
            role='admin',
        )
