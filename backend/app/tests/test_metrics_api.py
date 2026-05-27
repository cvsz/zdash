from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.api import metrics as metrics_api
from app.observability.metrics import metrics_store


def test_metrics_api_returns_prometheus_lines():
    metrics_store.increment_requests(12.5)
    metrics_store.increment_events(2)

    payload = metrics_api.metrics()
    assert "zdash_requests_total" in payload
    assert "zdash_request_latency_ms" in payload
    assert "zdash_events_total" in payload
    assert "zdash_scheduler_jobs_total" in payload
    assert "zdash_iot_actions_total" in payload


def test_metrics_auth_guard_blocks_when_required(monkeypatch):
    monkeypatch.setenv("METRICS_AUTH_REQUIRED", "true")
    monkeypatch.setenv("METRICS_ALLOW_UNAUTHENTICATED_DEV", "false")
    monkeypatch.setenv("AUTH_ENABLED", "false")
    monkeypatch.setenv("APP_ENV", "development")

    from app.core.config import get_settings

    get_settings.cache_clear()
    try:
        with pytest.raises(HTTPException) as exc_info:
            metrics_api._require_metrics_access(None)
        assert exc_info.value.status_code == 401
    finally:
        get_settings.cache_clear()
