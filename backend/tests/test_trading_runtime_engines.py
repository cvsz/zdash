from datetime import UTC, datetime, timedelta

import pytest

from app.trading.capital_preservation import CapitalPreservationGovernor
from app.trading.market_regime import MarketRegimeEngine
from app.trading.reconciliation_engine import ReconciliationEngine
from app.trading.trade_consensus import TradeConsensusEngine
from app.trading.tradingview_webhook import TradingViewWebhookValidator
from app.trading.trust_score import TrustScoreEngine


class _RiskEngine:
    def __init__(self, approve: bool = True) -> None:
        self.approve = approve

    def evaluate_order(self, order_req: dict) -> bool:
        return self.approve


# --- MarketRegimeEngine ------------------------------------------------------


def test_regime_normal_when_calm() -> None:
    engine = MarketRegimeEngine()
    assessment = engine.assess_regime(0.2, 0.8)
    assert assessment.regime == "normal"
    assert engine.current_regime == "normal"


def test_regime_volatile_and_crisis_thresholds() -> None:
    engine = MarketRegimeEngine()
    assert engine.assess_regime(0.6, 0.8).regime == "volatile"
    assert engine.assess_regime(0.9, 0.8).regime == "crisis"


def test_regime_fail_closed_on_unstable_exchange_and_thin_book() -> None:
    engine = MarketRegimeEngine()
    assert engine.assess_regime(0.1, 0.8, exchange_stable=False).regime == (
        "exchange_unstable"
    )
    assert engine.assess_regime(0.1, 0.1).regime == "illiquid"


def test_regime_rejects_out_of_range_inputs() -> None:
    engine = MarketRegimeEngine()
    with pytest.raises(ValueError):
        engine.assess_regime(1.5, 0.8)
    with pytest.raises(ValueError):
        engine.assess_regime(0.1, -0.1)


# --- CapitalPreservationGovernor ---------------------------------------------


def test_full_exposure_when_healthy() -> None:
    governor = CapitalPreservationGovernor()
    decision = governor.adjust_exposure(2.0, "normal")
    assert decision.max_exposure == 1.0
    assert decision.reason == "full_exposure"


def test_drawdown_contracts_exposure() -> None:
    governor = CapitalPreservationGovernor()
    decision = governor.adjust_exposure(11.0, "normal")
    assert decision.max_exposure == pytest.approx(0.5)
    assert decision.reason == "drawdown_contraction"


def test_crisis_regime_floors_exposure() -> None:
    governor = CapitalPreservationGovernor()
    for regime in ("crisis", "black_swan", "exchange_unstable"):
        governor = CapitalPreservationGovernor()
        decision = governor.adjust_exposure(0.0, regime)
        assert decision.max_exposure == pytest.approx(0.05)
        assert decision.reason == "crisis_floor"


def test_governor_rejects_invalid_bounds() -> None:
    with pytest.raises(ValueError):
        CapitalPreservationGovernor(max_exposure=0.0)
    governor = CapitalPreservationGovernor()
    with pytest.raises(ValueError):
        governor.adjust_exposure(-1.0, "normal")


# --- TradeConsensusEngine ----------------------------------------------------


def _regime_engine(regime: str) -> MarketRegimeEngine:
    engine = MarketRegimeEngine()
    engine.current_regime = regime  # type: ignore[assignment]
    return engine


def test_consensus_approves_strong_signal_in_normal_regime() -> None:
    consensus = TradeConsensusEngine(
        regime_engine=_regime_engine("normal"),
        risk_engine=_RiskEngine(True),
    )
    decision = consensus.validate_execution({"confidence": 0.9})
    assert decision.approved is True


def test_consensus_rejects_blocked_regimes() -> None:
    for regime in ("crisis", "black_swan", "exchange_unstable"):
        consensus = TradeConsensusEngine(regime_engine=_regime_engine(regime))
        assert consensus.validate_execution({"confidence": 0.99}).approved is False


def test_consensus_rejects_low_or_missing_confidence() -> None:
    consensus = TradeConsensusEngine(regime_engine=_regime_engine("normal"))
    assert consensus.validate_execution({"confidence": 0.4}).approved is False
    assert consensus.validate_execution({}).approved is False


def test_consensus_rejects_when_risk_engine_blocks() -> None:
    consensus = TradeConsensusEngine(
        regime_engine=_regime_engine("normal"),
        risk_engine=_RiskEngine(False),
    )
    decision = consensus.validate_execution({"confidence": 0.95})
    assert decision.approved is False
    assert "risk" in decision.reason


def test_consensus_fails_closed_without_regime_engine() -> None:
    consensus = TradeConsensusEngine()
    assert consensus.validate_execution({"confidence": 0.99}).approved is False


# --- TrustScoreEngine --------------------------------------------------------


def test_trust_score_weights() -> None:
    engine = TrustScoreEngine()
    result = engine.calculate_score(reconciliation_health=1.0, regime_stability=1.0)
    assert result.score == 1.0

    result = engine.calculate_score(reconciliation_health=0.0, regime_stability=1.0)
    assert result.score == pytest.approx(0.4)


def test_trust_score_rejects_out_of_range() -> None:
    engine = TrustScoreEngine()
    with pytest.raises(ValueError):
        engine.calculate_score(1.5, 0.5)
    with pytest.raises(ValueError):
        engine.calculate_score(0.5, -0.1)


# --- ReconciliationEngine ----------------------------------------------------


def test_reconciliation_healthy_when_sets_match() -> None:
    now = datetime.now(UTC)
    engine = ReconciliationEngine()
    report = engine.reconcile(
        local_orders={"o1": {"created_at": now}},
        venue_order_ids={"o1"},
        now=now,
    )
    assert report.healthy is True
    assert report.ghost_orders == []
    assert report.missing_orders == []


def test_reconciliation_detects_stale_ghost_orders() -> None:
    now = datetime.now(UTC)
    engine = ReconciliationEngine()
    report = engine.reconcile(
        local_orders={
            "fresh": {"created_at": now},
            "stale": {"created_at": now - timedelta(minutes=10)},
            "no_ts": {},
        },
        venue_order_ids={"fresh"},
        now=now,
    )
    assert report.healthy is False
    assert report.ghost_orders == ["no_ts", "stale"]


def test_reconciliation_detects_missing_orders() -> None:
    now = datetime.now(UTC)
    engine = ReconciliationEngine()
    report = engine.reconcile(
        local_orders={"o1": {"created_at": now}},
        venue_order_ids={"o1", "venue_only"},
        now=now,
    )
    assert report.healthy is False
    assert report.missing_orders == ["venue_only"]


# --- TradingViewWebhookValidator ---------------------------------------------


def _sign(secret: str, timestamp: int, payload: str) -> str:
    import hashlib
    import hmac

    return hmac.new(
        secret.encode(),
        f"{timestamp}.{payload}".encode(),
        hashlib.sha256,
    ).hexdigest()


def test_webhook_accepts_valid_signature() -> None:
    secret = "whsec_test"
    validator = TradingViewWebhookValidator(secret)
    ts = 1_700_000_000
    payload = '{"action":"buy"}'
    result = validator.validate_payload(_sign(secret, ts, payload), ts, payload, now=ts)
    assert result.valid is True
    assert result.reason == "accepted"


def test_webhook_rejects_bad_signature() -> None:
    validator = TradingViewWebhookValidator("whsec_test")
    result = validator.validate_payload(
        "deadbeef", 1_700_000_000, "{}", now=1_700_000_000
    )
    assert result.valid is False
    assert result.reason == "invalid_signature"


def test_webhook_rejects_expired_timestamp() -> None:
    secret = "whsec_test"
    validator = TradingViewWebhookValidator(secret)
    ts = 1_700_000_000
    payload = "{}"
    late = ts + 301
    result = validator.validate_payload(
        _sign(secret, ts, payload), ts, payload, now=late
    )
    assert result.valid is False
    assert result.reason == "timestamp_expired"


def test_webhook_fails_closed_without_secret() -> None:
    validator = TradingViewWebhookValidator(None)
    result = validator.validate_payload("sig", 1_700_000_000, "{}")
    assert result.valid is False
    assert result.reason == "missing_credentials"
