from app.content.policy import ContentPolicyChecker


def test_policy_rejects_empty_content() -> None:
    result = ContentPolicyChecker().check_text("")
    assert result["passed"] is False
    assert "empty_content" in result["blocked_terms"]


def test_policy_rejects_token_like_secret_pattern() -> None:
    result = ContentPolicyChecker().check_text("SOCIAL_X_API_KEY=abc123")
    assert result["passed"] is False
    assert "credential_or_private_key_pattern" in result["blocked_terms"]


def test_policy_rejects_guaranteed_profit_language() -> None:
    result = ContentPolicyChecker().check_text("Guaranteed profit with zero risk.")
    assert result["passed"] is False
    assert "guaranteed_profit_language" in result["blocked_terms"]


def test_policy_rejects_spam_hashtag_pattern() -> None:
    text = "#a #b #c #d #e #f #g #h #i"
    result = ContentPolicyChecker().check_text(text)
    assert result["passed"] is False
    assert "hashtag_spam" in result["blocked_terms"]


def test_policy_warns_trading_content_and_requires_disclaimer() -> None:
    result = ContentPolicyChecker().check_text("New backtest strategy results for markets.")
    assert result["passed"] is False
    assert "trading_content_detected" in result["warnings"]
    assert "missing_trading_disclaimer" in result["blocked_terms"]


def test_policy_accepts_safe_educational_trading_content() -> None:
    text = (
        "Backtesting strategy update for educational simulation only. "
        "Not financial advice. Past performance does not guarantee future results."
    )
    result = ContentPolicyChecker().check_text(text)
    assert result["passed"] is True
    assert "trading_content_detected" in result["warnings"]
