from __future__ import annotations

import pytest

from app.core.config import get_settings


def _settings(monkeypatch, **overrides):
    for k, v in overrides.items():
        monkeypatch.setenv(k, v)
    get_settings.cache_clear()


PROVIDER_CASES = [
    ("openrouter", "OPENROUTER_API_KEY", "OPENROUTER_MODEL", "openrouter/free"),
    ("kilo", "KILO_API_KEY", "KILO_MODEL", "auto"),
    ("opencode", "OPENCODE_API_KEY", "OPENCODE_MODEL", "opencode/grok-code"),
]

ADAPTER_CLASSES = {
    "openrouter": "OpenRouterAdapter",
    "kilo": "KiloAdapter",
    "opencode": "OpenCodeAdapter",
}


@pytest.mark.parametrize("provider,key_env,model_env,default_model", PROVIDER_CASES)
class TestOpenAICompatibleProviderContract:
    def _adapter(self, provider: str):
        import importlib

        module = importlib.import_module("app.ai.openai_compat_adapter")
        return getattr(module, ADAPTER_CLASSES[provider])()

    # --- missing dependency / credential: degrade to mock ------------------

    def test_missing_credential_falls_back_to_mock(
        self, monkeypatch, provider, key_env, model_env, default_model
    ):
        _settings(monkeypatch, **{key_env: ""})
        adapter = self._adapter(provider)
        assert adapter._should_fallback() is True
        result = adapter.generate_response("test")
        assert result.provider == "mock"

    def test_provider_disabled_returns_mock(
        self, monkeypatch, provider, key_env, model_env, default_model
    ):
        _settings(monkeypatch, AI_PROVIDER="mock", **{key_env: ""})
        adapter = self._adapter(provider)
        assert adapter.generate_response("test").provider == "mock"

    # --- configured: consistent safe response shape ------------------------

    def test_configured_placeholder_shape(
        self, monkeypatch, provider, key_env, model_env, default_model
    ):
        _settings(
            monkeypatch,
            **{key_env: "sk-test", model_env: default_model},
        )
        adapter = self._adapter(provider)
        assert adapter._should_fallback() is False
        result = adapter.generate_response("hello")
        assert result.provider == provider
        assert result.model == default_model
        assert isinstance(result.text, str) and result.text
        assert result.metadata.get("mode") == "placeholder"
        assert "base_url" in result.metadata

    def test_dry_run_true_has_no_side_effects(
        self, monkeypatch, provider, key_env, model_env, default_model
    ):
        from app.ai.factory import build_adapter

        _settings(monkeypatch, DRY_RUN="true", AI_PROVIDER=provider, **{key_env: ""})
        result = build_adapter(provider).generate_response("test")
        assert result.provider == "mock"


# --- factory routing ----------------------------------------------------------


@pytest.mark.parametrize(
    "provider",
    ["claude", "openrouter", "kilo", "opencode"],
)
def test_factory_routes_known_providers(monkeypatch, provider):
    from app.ai.factory import KNOWN_PROVIDERS, build_adapter

    assert provider in KNOWN_PROVIDERS
    adapter = build_adapter(provider)
    assert adapter is not None


def test_factory_unknown_provider_falls_back_to_mock():
    from app.ai.mock_adapter import MockAIAdapter
    from app.ai.factory import build_adapter

    assert isinstance(build_adapter("does-not-exist"), MockAIAdapter)


def test_registry_build_default_uses_ai_provider(monkeypatch):
    from app.agents.registry import build_default_ai_adapter
    from app.ai.openai_compat_adapter import OpenRouterAdapter

    _settings(monkeypatch, AI_PROVIDER="openrouter")
    # No key set -> the adapter itself degrades to mock at call time.
    assert isinstance(build_default_ai_adapter(), OpenRouterAdapter)


def test_trading_analysis_routes_new_providers(monkeypatch):
    from app.trading.ai_analysis import TradingAIAnalysis
    from app.ai.openai_compat_adapter import KiloAdapter

    _settings(monkeypatch, AI_TRADING_PROVIDER="kilo")
    analysis = TradingAIAnalysis()
    assert isinstance(analysis.adapter, KiloAdapter)


def test_settings_defaults_are_empty_and_safe(monkeypatch):
    for var in (
        "OPENROUTER_API_KEY",
        "KILO_API_KEY",
        "OPENCODE_API_KEY",
    ):
        monkeypatch.delenv(var, raising=False)
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.openrouter_api_key == ""
    assert settings.kilo_api_key == ""
    assert settings.opencode_api_key == ""
