import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.middleware.context import bind_request_context, clear_request_context


class RequestContextMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    user_id = request.headers.get("X-User-ID")

    clear_request_context()
    bind_request_context(request_id=request_id, user_id=user_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    clear_request_context()
    return response
