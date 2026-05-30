from __future__ import annotations

from app.core.config import get_settings


def validate_production_config() -> None:
    """Fail-closed startup validation for production mode.

    Must be called during application startup (lifespan).
    Raises RuntimeError if any safety invariant is violated,
    preventing the app from starting in an unsafe configuration.
    """
    settings = get_settings()
    if not settings.is_production:
        return

    errors: list[str] = []

    if not settings.auth_enabled:
        errors.append("AUTH_ENABLED must be true in production mode")

    if not settings.metrics_auth_required:
        errors.append("METRICS_AUTH_REQUIRED must be true in production mode")

    default_secret = "dev-only-change-before-production"
    if settings.jwt_secret_key.strip() in {"", default_secret}:
        errors.append("JWT_SECRET_KEY must not be default in production mode")

    if settings.default_admin_password.strip() in {"", default_secret}:
        errors.append("DEFAULT_ADMIN_PASSWORD must not be default in production mode")

    if settings.bootstrap_admin_password.strip() in {"", default_secret}:
        errors.append("BOOTSTRAP_ADMIN_PASSWORD must not be default in production mode")

    if not settings.dry_run and settings.production_safety_lock:
        errors.append("DRY_RUN must be true while PRODUCTION_SAFETY_LOCK is enabled")

    if "*" in settings.cors_origins_list and settings.cors_allow_credentials:
        errors.append("CORS wildcard + credentials is unsafe in production mode")

    if errors:
        raise RuntimeError(
            "Production safety validation failed:\n  - " + "\n  - ".join(errors)
        )
