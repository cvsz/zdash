from __future__ import annotations

import logging
import time
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.responses import fail
from app.observability.metrics import metrics_store

logger = logging.getLogger("zdash.observability")


def install_observability_middleware(app) -> None:
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000.0
        metrics_store.increment_requests(duration_ms)
        logger.info(
            "request.completed",
            extra={
                "context": {
                    "request_id": getattr(request.state, "request_id", ""),
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 3),
                }
            },
        )
        if response.status_code >= 400:
            metrics_store.increment_errors()
        return response

    @app.middleware("http")
    async def error_logging_middleware(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            metrics_store.increment_errors()
            logger.exception(
                "request.failed",
                extra={
                    "context": {
                        "request_id": getattr(request.state, "request_id", ""),
                        "method": request.method,
                        "path": request.url.path,
                        "error": type(exc).__name__,
                    }
                },
            )
            return JSONResponse(
                status_code=500,
                content=fail("INTERNAL_SERVER_ERROR", "Internal server error"),
            )
