#!/usr/bin/env python3
"""Fail-closed, standard-library check for operator-provided production configuration."""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlsplit


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:]
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        values[key.strip()] = value
    return values


def validate(values: dict[str, str]) -> list[str]:
    errors: list[str] = []
    required_flags = {
        "APP_ENV": "production",
        "AUTH_ENABLED": "true",
        "AUTH_ALLOW_BOOTSTRAP_IN_PRODUCTION": "false",
        "PRODUCTION_SAFETY_LOCK": "true",
        "PRODUCTION_ALLOW_LIVE_ACTIONS": "false",
        "DRY_RUN": "true",
        "RISK_GUARDIAN_ENABLED": "true",
        "SOCIAL_DRY_RUN": "true",
        "SOCIAL_AUTO_POST_ENABLED": "false",
        "IOT_DRY_RUN": "true",
        "METRICS_AUTH_REQUIRED": "true",
    }
    for key, expected in required_flags.items():
        if values.get(key, "").lower() != expected:
            errors.append(f"{key} must equal {expected}")

    for key, minimum in (
        ("JWT_SECRET_KEY", 32),
        ("POSTGRES_PASSWORD", 20),
        ("BOOTSTRAP_ADMIN_PASSWORD", 20),
        ("API_KEY_HASH_PEPPER", 32),
    ):
        value = values.get(key, "")
        if len(value) < minimum or any(
            marker in value.lower() for marker in ("dev-only", "change-me", "password", "sample")
        ):
            errors.append(f"{key} must contain a fresh non-example secret of at least {minimum} characters")

    url = values.get("DATABASE_URL", "")
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in {"postgresql+psycopg", "postgresql"}:
            errors.append("DATABASE_URL must use the production PostgreSQL driver")
        if not parsed.hostname or not parsed.username or not parsed.password:
            errors.append("DATABASE_URL must contain a PostgreSQL host, user and nonempty password")
        elif parsed.password != values.get("POSTGRES_PASSWORD"):
            errors.append("DATABASE_URL password must match POSTGRES_PASSWORD")
    except ValueError:
        errors.append("DATABASE_URL must be a valid PostgreSQL URL")

    origin = values.get("FRONTEND_ORIGIN", "").rstrip("/")
    if not origin.startswith("https://") or "*" in origin:
        errors.append("FRONTEND_ORIGIN must use an explicit HTTPS origin")

    cors = [x.strip() for x in values.get("CORS_ALLOW_ORIGINS", "").split(",") if x.strip()]
    if not cors or any(not x.startswith("https://") or "*" in x for x in cors):
        errors.append("CORS_ALLOW_ORIGINS must be an explicit HTTPS origin allowlist")
    if origin and cors and origin not in cors:
        errors.append("FRONTEND_ORIGIN must appear in CORS_ALLOW_ORIGINS")

    if values.get("DEFAULT_ADMIN_PASSWORD", "").lower().startswith(("dev-only", "change-me")):
        errors.append("DEFAULT_ADMIN_PASSWORD must not be a development example")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("env_file", type=Path, help="operator-managed production env file")
    args = parser.parse_args()
    if not args.env_file.is_file():
        parser.error("production environment file not found")
    errors = validate(load_env(args.env_file))
    if errors:
        for error in errors:
            print("BLOCKED:", error)
        return 1
    print("PASS: production config passed static checks; runtime, restore and edge evidence remain required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
