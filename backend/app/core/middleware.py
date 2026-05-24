from __future__ import annotations

import time
from collections import defaultdict, deque
from contextvars import ContextVar
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.observability import api_error_total, http_request_latency_seconds, http_requests_total

request_id_ctx: ContextVar[str] = ContextVar('request_id', default='')


class SimpleRateLimiter:
    def __init__(self, max_requests: int = 120, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.time()
        q = self._hits[key]
        while q and now - q[0] > self.window_seconds:
            q.popleft()
        if len(q) >= self.max_requests:
            return False
        q.append(now)
        return True


rate_limiter = SimpleRateLimiter()


def get_request_id() -> str:
    return request_id_ctx.get('')


def install_middleware(app):
    settings = get_settings()

    @app.middleware('http')
    async def request_context_middleware(request: Request, call_next):
        request_id = request.headers.get('x-request-id') or str(uuid4())
        correlation_id = request.headers.get('x-correlation-id') or request_id
        request_id_ctx.set(request_id)

        # Basic per-IP rate limiting stub for production safety.
        client_ip = request.client.host if request.client else 'unknown'
        limiter_key = f"{client_ip}:{request.url.path}"
        if not rate_limiter.allow(limiter_key):
            api_error_total.labels(code='RATE_LIMITED').inc()
            return JSONResponse(
                status_code=429,
                content={
                    'ok': False,
                    'data': None,
                    'error': {'code': 'RATE_LIMITED', 'message': 'Too many requests'},
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                },
                headers={'X-Request-ID': request_id, 'X-Correlation-ID': correlation_id},
            )

        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        response.headers['X-Request-ID'] = request_id
        response.headers['X-Correlation-ID'] = correlation_id

        path = request.url.path
        method = request.method
        status = str(response.status_code)
        http_requests_total.labels(method=method, path=path, status=status).inc()
        http_request_latency_seconds.labels(method=method, path=path).observe(duration)
        if response.status_code >= 400:
            api_error_total.labels(code=status).inc()
        return response

    # Restrict CORS in production unless explicitly set.
    if settings.app_env.lower() == 'production' and settings.cors_origins_list == ['*']:
        raise RuntimeError('CORS wildcard is not allowed in production.')
