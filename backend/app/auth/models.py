from datetime import datetime

from pydantic import BaseModel, Field


class AuthUser(BaseModel):
    username: str
    role: str


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class BootstrapAdminRequest(BaseModel):
    username: str | None = None
    password: str | None = None
    role: str = "admin"


class AccessTokenPayload(BaseModel):
    sub: str
    role: str
    exp: int
    type: str = "access"


class RefreshTokenPayload(BaseModel):
    sub: str
    role: str
    jti: str
    exp: int
    type: str = "refresh"


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    username: str


class AuthSession(BaseModel):
    username: str
    role: str
    expires_at: datetime | None = None
