from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4
from .models import InviteCode


class InviteService:
    def __init__(self) -> None:
        self._invites: dict[str, InviteCode] = {}

    def _hash(self, code: str) -> str:
        return sha256(code.encode()).hexdigest()

    def create_invite_code(self, request: dict) -> tuple[InviteCode, str]:
        raw = request.get("code") or str(uuid4()).split("-")[0]
        now = datetime.now(timezone.utc)
        invite = InviteCode(
            id=str(uuid4()),
            code_hash=self._hash(raw),
            label=request.get("label", ""),
            max_uses=request.get("max_uses", 1),
            created_by=request.get("created_by", "system"),
            created_at=now,
            updated_at=now,
        )
        self._invites[invite.id] = invite
        return invite, raw
