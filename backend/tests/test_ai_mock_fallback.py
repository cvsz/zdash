from app.ai.claude_adapter import ClaudeAdapter
from app.ai.mock_adapter import MockAIAdapter
from app.core.config import get_settings


def test_missing_claude_key_falls_back_to_mock(monkeypatch) -> None:
    monkeypatch.setenv("CLAUDE_API_KEY", "")
    monkeypatch.setenv("AI_PROVIDER", "claude")
    get_settings.cache_clear()

    adapter = ClaudeAdapter()
    result = adapter.generate_response("Status report", context={"source": "test"})

    assert result.provider == "mock"
    assert "[MOCK] Janie received:" in result.text
    get_settings.cache_clear()


def test_mock_adapter_is_deterministic() -> None:
    adapter = MockAIAdapter()
    r1 = adapter.generate_response("Ping", context={"a": 1, "b": 2})
    r2 = adapter.generate_response("Ping", context={"a": 1, "b": 2})

    assert r1.text == r2.text
    assert r1.provider == "mock"
