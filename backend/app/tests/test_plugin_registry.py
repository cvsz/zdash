from app.marketplace.builtins import BUILTINS
from app.marketplace.plugin_registry import get_plugin, list_plugins


def test_list_plugins():
    plugins = list_plugins()
    assert len(plugins) == len(BUILTINS)
    assert all(p in BUILTINS for p in plugins)


def test_get_plugin():
    for p in BUILTINS:
        found = get_plugin(p.id)
        assert found is not None
        assert found.id == p.id

    assert get_plugin("non-existent-plugin") is None
