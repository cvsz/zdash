from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from app.core.config import get_settings
from app.core.events import event_bus
from app.risk.models import HaltState


class HaltFlagStore:
    def __init__(self) -> None:
        self._state = HaltState()
        self._lock = Lock()
        self._settings = get_settings()

    def get_state(self) -> HaltState:
        with self._lock:
            return self._state.model_copy(deep=True)

    def is_halted(self) -> bool:
        return self.get_state().halted

    def halt(self, reason: str, source: str) -> HaltState:
        clean_reason = (reason or '').strip()
        clean_source = (source or '').strip()
        if not clean_reason:
            raise ValueError('Halt reason is required.')
        if not clean_source:
            raise ValueError('Halt source is required.')

        now = datetime.now(timezone.utc)
        with self._lock:
            self._state = HaltState(
                halted=True,
                reason=clean_reason,
                source=clean_source,
                created_at=now,
                resumed_at=None,
                resume_reason=None,
            )
            state = self._state.model_copy(deep=True)

        event_bus.emit(
            'risk.halt.activated',
            'HaltFlagStore',
            'Risk halt activated',
            {'reason': clean_reason, 'source': clean_source},
        )
        return state

    def resume(self, reason: str) -> HaltState:
        clean_reason = (reason or '').strip()
        if self._settings.require_resume_reason and not clean_reason:
            raise ValueError('Resume reason is required.')

        now = datetime.now(timezone.utc)
        with self._lock:
            current = self._state.model_copy(deep=True)
            self._state = HaltState(
                halted=False,
                reason=current.reason,
                source=current.source,
                created_at=current.created_at,
                resumed_at=now,
                resume_reason=clean_reason or current.resume_reason,
            )
            state = self._state.model_copy(deep=True)

        event_bus.emit(
            'risk.halt.resumed',
            'HaltFlagStore',
            'Risk halt resumed',
            {'reason': clean_reason},
        )
        return state

    def clear(self) -> None:
        with self._lock:
            self._state = HaltState()


halt_store = HaltFlagStore()
