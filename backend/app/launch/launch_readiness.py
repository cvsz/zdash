from app.core.config import get_settings


class LaunchReadinessService:
    def run_all_checks(self) -> dict:
        s = get_settings()
        checks = {
            "dry_run_default_safe": bool(s.dry_run),
            "guardian_enabled": bool(s.risk_guardian_enabled),
            "iot_dry_run_enabled": bool(s.iot_dry_run),
            "social_dry_run_enabled": bool(s.social_dry_run),
        }
        blockers = [k for k, v in checks.items() if not v]
        return {"checks": checks, "blockers": blockers, "score": (len(checks)-len(blockers))*100//len(checks)}
