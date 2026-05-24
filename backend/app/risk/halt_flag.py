from dataclasses import dataclass

from app.core.database import session_scope
from app.repositories import Repository


@dataclass
class HaltState:
    halted: bool = False
    reason: str = ''
    updated_at: str = ''
    locked: bool = False


def get_halt_state() -> HaltState:
    with session_scope() as session:
        row = Repository(session).latest_halt_flag()
    if row is None:
        return HaltState()
    return HaltState(halted=row.halted, reason=row.reason, updated_at=row.created_at.isoformat(), locked=row.locked)


def set_halt(reason: str, actor: str = 'system', locked: bool = False) -> HaltState:
    with session_scope() as session:
        Repository(session).set_halt_flag(halted=True, reason=reason, actor=actor, locked=locked)
    return get_halt_state()


def clear_halt(reason: str, actor: str = 'system') -> HaltState:
    current = get_halt_state()
    if current.locked:
        return current
    with session_scope() as session:
        Repository(session).set_halt_flag(halted=False, reason=reason, actor=actor, locked=False)
    return get_halt_state()
