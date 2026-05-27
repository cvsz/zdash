from __future__ import annotations

import re


class ContentPolicyChecker:
    _credential_patterns = (
        re.compile(r"\b[\w-]*api[_-]?key\b\s*[:=]", re.IGNORECASE),
        re.compile(r"\b[\w-]*access[_-]?token\b\s*[:=]", re.IGNORECASE),
        re.compile(r"\bpassword\b\s*[:=]", re.IGNORECASE),
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
    )
    _guaranteed_profit_pattern = re.compile(
        r"guaranteed\s+profit|risk[- ]?free\s+profit|100%\s+win|no[- ]loss",
        re.IGNORECASE,
    )
    _impersonation_pattern = re.compile(
        r"\bi am (official|your)\b|\bofficial (broker|support)\b|"
        r"\bact as your broker\b",
        re.IGNORECASE,
    )
    _hashtag_spam_pattern = re.compile(r"(#\w+\s*){8,}", re.IGNORECASE)
    _emoji_pattern = re.compile(r"[\U0001F300-\U0001FAFF]")
    _url_pattern = re.compile(r"https?://\S+", re.IGNORECASE)
    _trading_pattern = re.compile(
        r"\btrading?\b|\bmarket(s)?\b|\bstrategy\b|\bbacktest(ing)?\b|\bresults?\b",
        re.IGNORECASE,
    )
    _disclaimer_pattern = re.compile(
        r"educational|simulation|paper[- ]?trading|not financial advice|"
        r"past performance does not guarantee future results|"
        r"backtest results are not guaranteed future performance",
        re.IGNORECASE,
    )

    def check_text(self, text: str, context: dict | None = None) -> dict:
        _ = context or {}
        t = (text or "").strip()
        notes: list[str] = []
        blocked: list[str] = []
        warnings: list[str] = []

        if not t:
            blocked.append("empty_content")
            notes.append("Empty content is not allowed.")

        if any(pattern.search(t) for pattern in self._credential_patterns):
            blocked.append("credential_or_private_key_pattern")
            notes.append("Potential credential leakage detected.")

        if self._guaranteed_profit_pattern.search(t):
            blocked.append("guaranteed_profit_language")
            notes.append("Misleading guaranteed-profit language detected.")

        if self._impersonation_pattern.search(t):
            blocked.append("impersonation_language")
            notes.append("Impersonation language detected.")

        if self._hashtag_spam_pattern.search(t):
            blocked.append("hashtag_spam")
            notes.append("Excessive hashtag pattern detected.")

        if len(self._emoji_pattern.findall(t)) >= 8:
            blocked.append("emoji_spam")
            notes.append("Excessive emoji usage detected.")

        if len(self._url_pattern.findall(t)) >= 4:
            blocked.append("link_spam")
            notes.append("Excessive link usage detected.")

        if self._trading_pattern.search(t):
            warnings.append("trading_content_detected")
            if not self._disclaimer_pattern.search(t):
                warnings.append("missing_risk_disclaimer")
                blocked.append("missing_trading_disclaimer")
                notes.append(
                    "Trading/backtesting/strategy content must include educational "
                    "or simulation disclaimer text."
                )

        passed = len(blocked) == 0
        return {
            "passed": passed,
            "notes": notes,
            "blocked_terms": blocked,
            "warnings": warnings,
        }
