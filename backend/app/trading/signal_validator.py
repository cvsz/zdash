from app.trading.risk_models import Signal


class SignalValidator:
    def validate(self, signal: Signal) -> dict:
        issues: list[str] = []
        if signal.direction == 'neutral':
            issues.append('Direction is neutral.')
        if signal.confidence < 0.55:
            issues.append('Confidence below threshold 0.55.')

        entry_mid = (signal.entry_zone[0] + signal.entry_zone[1]) / 2
        risk = abs(entry_mid - signal.stop_loss)
        reward = abs(signal.take_profit - entry_mid)
        rr = reward / risk if risk > 0 else 0
        if rr < 1.2:
            issues.append('Risk reward below 1.2.')

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'risk_reward': round(rr, 4),
        }
