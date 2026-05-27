from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

http_requests_total = Counter(
    "zdash_http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)
http_request_latency_seconds = Histogram(
    "zdash_http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)
api_error_total = Counter("zdash_api_error_total", "API errors", ["code"])
trading_scan_total = Counter("zdash_trading_scan_total", "Trading scan count")
signal_validation_total = Counter(
    "zdash_signal_validation_total", "Signal validation count", ["valid"]
)
execution_blocked_total = Counter(
    "zdash_execution_blocked_total", "Execution blocked count"
)
risk_halt_total = Counter("zdash_risk_halt_total", "Risk halt count", ["type"])
scheduler_job_total = Counter(
    "zdash_scheduler_job_total", "Scheduler job actions", ["action"]
)
content_pipeline_action_total = Counter(
    "zdash_content_pipeline_action_total", "Content pipeline action count", ["action"]
)
auth_login_total = Counter("zdash_auth_login_total", "Auth login count", ["status"])


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
