import pytest

from app.risk.halt_flag import HaltFlagStore


def test_initial_state_not_halted() -> None:
    store = HaltFlagStore()
    state = store.get_state()
    assert state.halted is False


def test_halt_activates() -> None:
    store = HaltFlagStore()
    state = store.halt(reason='manual pause', source='test')
    assert state.halted is True
    assert state.reason == 'manual pause'
    assert state.source == 'test'


def test_resume_clears_halt() -> None:
    store = HaltFlagStore()
    store.halt(reason='manual pause', source='test')
    resumed = store.resume(reason='reviewed safe')
    assert resumed.halted is False
    assert resumed.resume_reason == 'reviewed safe'


def test_reason_required() -> None:
    store = HaltFlagStore()
    with pytest.raises(ValueError):
        store.halt(reason='', source='test')


def test_source_required() -> None:
    store = HaltFlagStore()
    with pytest.raises(ValueError):
        store.halt(reason='ok', source='')
