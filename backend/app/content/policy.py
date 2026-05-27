from __future__ import annotations

import re


class ContentPolicyChecker:
    def check_text(self, text: str, context: dict | None = None) -> dict:
        t = (text or "").strip()
        notes: list[str] = []
        blocked: list[str] = []
        warnings: list[str] = []
        if not t:
            blocked.append("empty_content")
            notes.append("Empty content is not allowed.")
        patterns = [
            r"api[_-]?key\s*[:=]",
            r"access[_-]?token\s*[:=]",
            r"password\s*[:=]",
            r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----",
        ]
        if any(re.search(p, t, re.IGNORECASE) for p in patterns):
            blocked.append("credential_leak")
            notes.append("Potential credential leakage detected.")
        if re.search(
            r"guaranteed\s+profit|risk[- ]?free\s+profit|100%\s+win", t, re.IGNORECASE
        ):
            blocked.append("misleading_profit_claim")
            notes.append("Misleading guaranteed-profit language detected.")
        if re.search(
            r"official\s+zDash\s+support\s+agent|i\s+am\s+your\s+broker",
            t,
            re.IGNORECASE,
        ):
            blocked.append("impersonation")
        if re.search(r"(#\w+\s*){8,}", t):
            blocked.append("hashtag_spam")
        if len(re.findall(r"[\U0001F300-\U0001FAFF]", t)) >= 8:
            blocked.append("emoji_spam")
        if len(re.findall(r"https?://\S+", t)) >= 4:
            blocked.append("link_spam")
        if re.search(r"trad(e|ing)|market|backtest|strategy", t, re.IGNORECASE):
            warnings.append("trading_content_detected")
            if not re.search(
                r"educational|not financial advice|simulation|past performance",
                t,
                re.IGNORECASE,
            ):
                warnings.append("missing_risk_disclaimer")
        passed = not blocked
        if not passed:
            notes.extend(blocked)
        return {
            "passed": passed,
            "notes": notes,
            "blocked_terms": blocked,
            "warnings": warnings,
        }
