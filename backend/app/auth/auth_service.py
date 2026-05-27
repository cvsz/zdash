from __future__ import annotations

from hashlib import sha256

from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.models import TokenPair
from app.auth.password import hash_password, verify_password
from app.core.config import get_settings
from app.db.repositories import RefreshTokenRepository, UserRepository


class AuthService:
    def __init__(self, users: UserRepository, refresh_tokens: RefreshTokenRepository):
        self.users = users
        self.refresh_tokens = refresh_tokens
        self.settings = get_settings()

    @staticmethod
    def _hash_token(token: str) -> str:
        return sha256(token.encode("utf-8")).hexdigest()

    def _build_token_pair(self, username: str, role: str, user_id: str) -> TokenPair:
        access_token = create_access_token(username, role)
        refresh_token = create_refresh_token(username, role)
        self.refresh_tokens.create(user_id=user_id, token_hash=self._hash_token(refresh_token))
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            role=role,
            username=username,
        )

    def login(self, username: str, password: str) -> TokenPair | None:
        user = self.users.get_by_email(username)
        if user is None or not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return self._build_token_pair(username=user.email, role=user.role, user_id=user.id)

    def refresh(self, refresh_token: str) -> TokenPair | None:
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            return None
        if payload.get("type") != "refresh":
            return None
        token_hash = self._hash_token(refresh_token)
        stored = self.refresh_tokens.get(token_hash)
        if stored is None or stored.is_revoked:
            return None
        user = self.users.get_by_id(stored.user_id)
        if user is None or not user.is_active:
            return None
        self.refresh_tokens.revoke(token_hash)
        return self._build_token_pair(username=user.email, role=user.role, user_id=user.id)

    def logout(self, refresh_token: str) -> bool:
        token_hash = self._hash_token(refresh_token)
        return self.refresh_tokens.revoke(token_hash)

    def bootstrap_admin(self, username: str | None, password: str | None) -> tuple[bool, str]:
        if self.users.count() > 0:
            return False, "Admin bootstrap is only allowed when no users exist."
        if self.settings.is_production and not self.settings.auth_allow_bootstrap_in_production:
            return False, "Admin bootstrap is disabled in production."

        bootstrap_username = (username or self.settings.bootstrap_admin_username).strip()
        bootstrap_password = (password or self.settings.bootstrap_admin_password).strip()
        if not bootstrap_username:
            return False, "Bootstrap username is required."
        if not bootstrap_password:
            return False, "Bootstrap password is required."

        self.users.create(
            email=bootstrap_username,
            password_hash=hash_password(bootstrap_password),
            role="admin",
            display_name="Administrator",
        )
        return True, bootstrap_username
