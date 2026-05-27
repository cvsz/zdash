from app.realtime.ws_manager import WebSocketManager


def test_ws_manager_alias_import() -> None:
    manager = WebSocketManager()
    assert manager.snapshot()["total"] == 0
