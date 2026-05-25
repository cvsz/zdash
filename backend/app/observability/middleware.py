from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['X-Request-ID'] = str(uuid.uuid4())
        return response
