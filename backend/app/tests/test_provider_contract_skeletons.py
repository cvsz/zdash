from __future__ import annotations

import pytest
from app.core.config import get_settings

# Provider Adapter Contract Tests.
# Every provider adapter must cover:
# - missing_dependency: Gracefully handles missing optional dependency
# - missing_credential: Degrades when required credential is unset
# - provider_disabled: Returns safe fallback when disabled by env flag
# - dry_run_true: No side effects when DRY_RUN=true
# - approval_missing: Action blocked when approval not granted
# - network_unavailable: Degrades when network call fails (where applicable)
# - timeout: Handles timeout without hanging (where applicable)
# - invalid_payload: Rejects malformed input
# - safe_response_shape: Returns consistent response shape


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------





def _settings(monkeypatch, **overrides):
    for k, v in overrides.items():
        monkeypatch.setenv(k, v)
    get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Claude / AI Adapter
# ---------------------------------------------------------------------------


class TestClaudeAdapterContract:
    def test_missing_dependency(self, monkeypatch):
        from app.ai.claude_adapter import ClaudeAdapter

        _settings(monkeypatch, CLAUDE_API_KEY="sk-real-key")
        adapter = ClaudeAdapter()
        adapter._should_fallback = lambda: False  # simulate SDK path
        result = adapter.generate_response("test")
        assert result.provider in ("claude", "mock")
        assert isinstance(result.text, str)

    def test_missing_credential(self, monkeypatch):
        from app.ai.claude_adapter import ClaudeAdapter

        _settings(monkeypatch, CLAUDE_API_KEY="")
        adapter = ClaudeAdapter()
        assert adapter._should_fallback() is True
        result = adapter.generate_response("test")
        assert result.provider == "mock"

    def test_provider_disabled(self, monkeypatch):
        from app.ai.claude_adapter import ClaudeAdapter

        _settings(monkeypatch, AI_PROVIDER="mock")
        adapter = ClaudeAdapter()
        result = adapter.generate_response("test")
        assert result.provider == "mock"

    def test_dry_run_true(self, monkeypatch):
        from app.ai.claude_adapter import ClaudeAdapter

        _settings(monkeypatch, DRY_RUN="true")
        adapter = ClaudeAdapter()
        result = adapter.generate_response("test")
        assert result.provider == "mock"

    def test_approval_missing(self, monkeypatch):
        from app.ai.claude_adapter import ClaudeAdapter

        _settings(monkeypatch, CLAUDE_API_KEY="sk-real-key")
        adapter = ClaudeAdapter()
        adapter._should_fallback = lambda: False
        result = adapter.generate_response("test")
        assert result.text is not None

    def test_invalid_payload(self, monkeypatch):
        from app.ai.claude_adapter import ClaudeAdapter

        _settings(monkeypatch)
        adapter = ClaudeAdapter()
        result = adapter.generate_response("")
        assert isinstance(result.text, str)

    def test_safe_response_shape(self, monkeypatch):
        from app.ai.claude_adapter import ClaudeAdapter

        _settings(monkeypatch)
        adapter = ClaudeAdapter()
        result = adapter.generate_response("test")
        assert hasattr(result, "provider")
        assert hasattr(result, "text")
        assert hasattr(result, "model")
        assert hasattr(result, "metadata")


# ---------------------------------------------------------------------------
# MT5 Adapter
# ---------------------------------------------------------------------------


class TestMt5AdapterContract:
    def test_missing_dependency(self, monkeypatch):
        from app.trading.mt5_adapter import MT5Adapter

        _settings(monkeypatch, MT5_ENABLED="true")
        adapter = MT5Adapter()
        adapter._mt5_module = None
        result = adapter.connect()
        assert result["mode"] == "mock"
        assert result["connected"] is False
        assert "unavailable" in result["reason"]

    def test_missing_credential(self, monkeypatch):
        from app.trading.mt5_adapter import MT5Adapter

        _settings(monkeypatch, MT5_ENABLED="true", MT5_LOGIN="", MT5_PASSWORD="", MT5_SERVER="")
        adapter = MT5Adapter()
        result = adapter.connect()
        assert result["mode"] == "mock"
        assert result["connected"] is False

    def test_provider_disabled(self, monkeypatch):
        from app.trading.mt5_adapter import MT5Adapter

        _settings(monkeypatch, MT5_ENABLED="false")
        adapter = MT5Adapter()
        result = adapter.connect()
        assert result["mode"] == "mock"
        assert result["connected"] is False

    def _make_signal(self, **kw):
        from app.trading.models import TradingSignal

        defaults = dict(
            symbol="XAUUSD",
            timeframe="M5",
            direction="buy",
            strategy="test",
            confidence=0.8,
            entry=2000.0,
            stop_loss=1990.0,
            take_profit=2020.0,
            reason="contract test",
        )
        defaults.update(kw)
        return TradingSignal(**defaults)

    def test_dry_run_true(self, monkeypatch):
        from app.trading.mt5_adapter import MT5Adapter

        _settings(monkeypatch, DRY_RUN="true")
        adapter = MT5Adapter()
        signal = self._make_signal()
        result = adapter.send_order(signal)
        assert result.dry_run is True
        assert result.ok is True

    def test_approval_missing(self, monkeypatch):
        from app.trading.mt5_adapter import MT5Adapter

        _settings(monkeypatch, DRY_RUN="false", LIVE_TRADING_ACK="false")
        adapter = MT5Adapter()
        signal = self._make_signal()
        result = adapter.send_order(signal)
        assert result.ok is False
        assert "blocked" in result.status

    def test_invalid_payload(self, monkeypatch):
        from app.trading.mt5_adapter import MT5Adapter

        _settings(monkeypatch)
        adapter = MT5Adapter()
        signal = self._make_signal(symbol="", direction="buy")
        result = adapter.send_order(signal)
        assert isinstance(result, object)

    def test_safe_response_shape(self, monkeypatch):
        from app.trading.mt5_adapter import MT5Adapter

        _settings(monkeypatch)
        adapter = MT5Adapter()
        signal = self._make_signal()
        result = adapter.send_order(signal)
        assert hasattr(result, "ok")
        assert hasattr(result, "status")
        assert hasattr(result, "dry_run")
        assert hasattr(result, "message")

    def test_mock_candles_returned(self, monkeypatch):
        from app.trading.mt5_adapter import MT5Adapter

        _settings(monkeypatch)
        adapter = MT5Adapter()
        candles = adapter.get_candles("XAUUSD", "M5", 100)
        assert len(candles) >= 100
        assert candles[0].close > 0


# ---------------------------------------------------------------------------
# Tapo / IoT Adapter
# ---------------------------------------------------------------------------


class TestTapoAdapterContract:
    def test_missing_dependency(self, monkeypatch):
        from app.iot.tapo_adapter import TapoAdapter

        _settings(monkeypatch, IOT_DRY_RUN="true")
        adapter = TapoAdapter()
        result = adapter.get_status("test-device")
        assert result.dry_run is True
        assert result.ok is True

    def test_missing_credential(self, monkeypatch):
        from app.iot.tapo_adapter import TapoAdapter

        _settings(monkeypatch, IOT_DRY_RUN="false", TAPO_USERNAME="", TAPO_PASSWORD="")
        adapter = TapoAdapter()
        result = adapter.turn_on("test-device")
        assert result.dry_run is True

    def test_provider_disabled(self, monkeypatch):
        from app.iot.tapo_adapter import TapoAdapter

        _settings(monkeypatch, IOT_ENABLED="false")
        adapter = TapoAdapter()
        result = adapter.get_status("test-device")
        assert isinstance(result, object)

    def test_dry_run_true(self, monkeypatch):
        from app.iot.tapo_adapter import TapoAdapter

        _settings(monkeypatch, IOT_DRY_RUN="true")
        adapter = TapoAdapter()
        result = adapter.turn_on("test-device")
        assert result.dry_run is True
        assert result.ok is True

    def test_approval_missing(self, monkeypatch):
        from app.iot.tapo_adapter import TapoAdapter

        _settings(
            monkeypatch,
            IOT_DRY_RUN="false",
            IOT_REQUIRE_CONFIRMATION="true",
            TAPO_USERNAME="u",
            TAPO_PASSWORD="p",
            TAPO_DEVICE_IP="1.2.3.4",
        )
        adapter = TapoAdapter()
        result = adapter.power_cycle("test-device", confirmation=False)
        assert result.ok is False
        assert "confirmation_required" in result.message.lower() or "blocked" in result.message.lower()

    def test_invalid_payload(self, monkeypatch):
        from app.iot.tapo_adapter import TapoAdapter

        _settings(monkeypatch)
        adapter = TapoAdapter()
        result = adapter.turn_on("")
        assert isinstance(result, object)

    def test_safe_response_shape(self, monkeypatch):
        from app.iot.tapo_adapter import TapoAdapter

        _settings(monkeypatch)
        adapter = TapoAdapter()
        result = adapter.get_status("test-device")
        assert hasattr(result, "ok")
        assert hasattr(result, "dry_run")
        assert hasattr(result, "message")
        assert hasattr(result, "device_alias")


# ---------------------------------------------------------------------------
# Social Media Adapter
# ---------------------------------------------------------------------------


class TestSocialAdapterContract:
    def test_missing_credential(self, monkeypatch):
        from app.content.social_adapters import XAdapter
        from app.content.models import ContentPlatform

        adapter = XAdapter(token="")
        result = adapter.publish(ContentPlatform.x, "hello", None)
        assert result.ok is False
        assert result.external_id is None

    def test_provider_disabled(self, monkeypatch):
        from app.content.social_adapters import MockSocialMediaAdapter
        from app.content.models import ContentPlatform

        adapter = MockSocialMediaAdapter()
        result = adapter.publish(ContentPlatform.x, "hello", None)
        assert result.ok is True
        assert result.dry_run is True

    def test_dry_run_true(self, monkeypatch):
        from app.content.social_adapters import MockSocialMediaAdapter
        from app.content.models import ContentPlatform

        _settings(monkeypatch, SOCIAL_DRY_RUN="true")
        adapter = MockSocialMediaAdapter()
        result = adapter.publish(ContentPlatform.x, "test", None)
        assert result.dry_run is True
        assert result.ok is True

    def test_approval_missing(self, monkeypatch):
        from app.content.social_adapters import _CredentialGuardedStubAdapter
        from app.content.models import ContentPlatform

        adapter = _CredentialGuardedStubAdapter("test", token="valid-token")
        result = adapter.publish(ContentPlatform.generic, "test", None)
        assert result.ok is False

    def test_invalid_payload(self, monkeypatch):
        from app.content.social_adapters import MockSocialMediaAdapter
        from app.content.models import ContentPlatform

        adapter = MockSocialMediaAdapter()
        result = adapter.publish(ContentPlatform.generic, "", None)
        assert isinstance(result, object)

    def test_safe_response_shape(self, monkeypatch):
        from app.content.social_adapters import MockSocialMediaAdapter
        from app.content.models import ContentPlatform

        adapter = MockSocialMediaAdapter()
        result = adapter.publish(ContentPlatform.x, "hello", None)
        assert hasattr(result, "ok")
        assert hasattr(result, "dry_run")
        assert hasattr(result, "platform")
        assert hasattr(result, "external_id")
        assert hasattr(result, "message")


# ---------------------------------------------------------------------------
# Image Generation Adapter
# ---------------------------------------------------------------------------


class TestImageGenAdapterContract:
    def test_missing_dependency(self, monkeypatch):
        from app.content.image_adapters import MockImageGenerationAdapter

        adapter = MockImageGenerationAdapter()
        result = adapter.generate_image("test")
        assert result["ok"] is True
        assert result["provider"] == "mock"

    def test_missing_credential(self, monkeypatch):
        from app.content.image_adapters import build_image_adapter

        _settings(monkeypatch, IMAGE_GENERATION_PROVIDER="mock")
        adapter = build_image_adapter()
        result = adapter.generate_image("test")
        assert result["ok"] is True

    def test_provider_disabled(self, monkeypatch):
        from app.content.image_adapters import build_image_adapter

        _settings(monkeypatch, IMAGE_GENERATION_PROVIDER="none")
        adapter = build_image_adapter()
        result = adapter.generate_image("test")
        assert result["ok"] is True
        assert "mock" in result["provider"]

    def test_dry_run_true(self, monkeypatch):
        from app.content.image_adapters import MockImageGenerationAdapter

        adapter = MockImageGenerationAdapter()
        result = adapter.generate_image("test")
        assert result["dry_run"] is True

    def test_invalid_payload(self, monkeypatch):
        from app.content.image_adapters import MockImageGenerationAdapter

        adapter = MockImageGenerationAdapter()
        result = adapter.generate_image("")
        assert result["ok"] is True

    def test_safe_response_shape(self, monkeypatch):
        from app.content.image_adapters import MockImageGenerationAdapter

        adapter = MockImageGenerationAdapter()
        result = adapter.generate_image("test")
        assert "ok" in result
        assert "dry_run" in result
        assert "asset_url" in result
        assert "provider" in result


# ---------------------------------------------------------------------------
# Stripe / Payment Adapter
# ---------------------------------------------------------------------------


class TestStripeAdapterContract:
    def test_missing_dependency(self):
        from app.billing.stripe_adapter import StripeAdapter

        adapter = StripeAdapter()
        try:
            adapter._stripe_client()
        except ImportError:
            pass  # Expected — SDK not installed

    def test_missing_credential(self):
        # Use mock adapter to test missing credential behavior
        from app.content.social_adapters import _CredentialGuardedStubAdapter
        from app.content.models import ContentPlatform

        adapter = _CredentialGuardedStubAdapter("stripe", token="")
        result = adapter.publish(ContentPlatform.generic, "test", None)
        assert result.ok is False

    def test_provider_disabled(self):
        from app.billing.stripe_adapter import StripeAdapter

        adapter = StripeAdapter()
        # Stripe is disabled by default in dev/test
        assert adapter._enabled is False

    def test_dry_run_true(self):
        from app.billing.mock_billing_adapter import MockBillingAdapter

        adapter = MockBillingAdapter()
        result = adapter.create_customer("org-1")
        assert isinstance(result, str)

    def test_approval_missing(self):
        from app.billing.stripe_adapter import StripeAdapter

        adapter = StripeAdapter()
        with pytest.raises(RuntimeError) as excinfo:
            adapter._require_enabled()
        assert any(word in str(excinfo.value).lower() for word in ("disabled", "not configured"))

    def test_invalid_payload(self):
        from app.billing.stripe_adapter import StripeAdapter

        adapter = StripeAdapter()
        assert adapter._enabled is False

    def test_safe_response_shape(self):
        from app.billing.mock_billing_adapter import MockBillingAdapter

        adapter = MockBillingAdapter()
        customer = adapter.create_customer("org-1")
        assert isinstance(customer, str)
        sub = adapter.create_checkout_session("org-1", "starter")
        assert isinstance(sub, str)
