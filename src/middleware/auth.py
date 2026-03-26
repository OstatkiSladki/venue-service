from datetime import datetime, timezone

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core_exceptions import AppError, UnauthorizedError
from src.schemas.common import IdentityContext, UserRole


class GatewayAuthMiddleware(BaseHTTPMiddleware):
    _BYPASS_PATHS = {"/health", "/ready", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        try:
            if request.url.path in self._BYPASS_PATHS:
                return await call_next(request)

            user_id = request.headers.get("X-User-ID")
            user_role_raw = request.headers.get("X-User-Role")
            request_id = request.headers.get("X-Request-ID")
            venue_id_raw = request.headers.get("X-User-Venue-ID")

            if not user_id or not user_role_raw or not request_id:
                raise UnauthorizedError("Missing gateway identity headers")

            try:
                role = UserRole(user_role_raw)
            except ValueError as exc:
                raise UnauthorizedError("Invalid X-User-Role header") from exc

            venue_id: int | None = None
            if venue_id_raw is not None:
                try:
                    venue_id = int(venue_id_raw)
                except ValueError as exc:
                    raise UnauthorizedError("Invalid X-User-Venue-ID header") from exc

            request.state.identity = IdentityContext(
                user_id=user_id,
                role=role,
                request_id=request_id,
                venue_id=venue_id,
            )
            return await call_next(request)
        except AppError as exc:
            payload = {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details or [],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": request.headers.get("X-Request-ID"),
                "trace_id": None,
            }
            return JSONResponse(status_code=exc.status_code, content=payload)
