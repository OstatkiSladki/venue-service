from typing import Annotated
from typing import cast

from fastapi import Depends, Request, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from src.core_exceptions import ForbiddenError, UnauthorizedError
from src.db.session import get_db_session
from src.events.publisher import EventPublisher, NoopEventPublisher
from src.schemas.common import IdentityContext, UserRole
from src.services.company_service import CompanyService
from src.services.payout_service import PayoutService
from src.services.venue_service import VenueService


x_user_id_header = APIKeyHeader(name="X-User-ID", scheme_name="X-User-ID", auto_error=False)
x_user_role_header = APIKeyHeader(name="X-User-Role", scheme_name="X-User-Role", auto_error=False)
x_request_id_header = APIKeyHeader(name="X-Request-ID", scheme_name="X-Request-ID", auto_error=False)
x_user_venue_id_header = APIKeyHeader(name="X-User-Venue-ID", scheme_name="X-User-Venue-ID", auto_error=False)

def _require_header(name: str, value: str | None) -> str:
    if not value:
        raise UnauthorizedError(f"{name} header is required")
    return value

async def get_optional_identity_context(
    x_user_id: str | None = Security(x_user_id_header),
    x_user_role: str | None = Security(x_user_role_header),
    x_request_id: str | None = Security(x_request_id_header),
    x_user_venue_id: str | None = Security(x_user_venue_id_header),
) -> IdentityContext | None:
    if not x_user_id or not x_user_role:
        return None

    request_id = x_request_id or "unknown-request"
    
    try:
        role = UserRole(x_user_role)
    except ValueError as exc:
        raise UnauthorizedError("Invalid X-User-Role header") from exc

    venue_id: int | None = None
    if x_user_venue_id is not None:
        try:
            venue_id = int(x_user_venue_id)
        except ValueError as exc:
            raise UnauthorizedError("Invalid X-User-Venue-ID header") from exc

    return IdentityContext(
        user_id=x_user_id,
        role=role,
        request_id=request_id,
        venue_id=venue_id,
    )

async def get_identity_context(
    x_user_id: str | None = Security(x_user_id_header),
    x_user_role: str | None = Security(x_user_role_header),
    x_request_id: str | None = Security(x_request_id_header),
    x_user_venue_id: str | None = Security(x_user_venue_id_header),
) -> IdentityContext:
    request_id = x_request_id or "unknown-request"
    user_id = _require_header("X-User-ID", x_user_id)
    role_str = _require_header("X-User-Role", x_user_role)
    _require_header("X-Request-ID", x_request_id)
    
    try:
        role = UserRole(role_str)
    except ValueError as exc:
        raise UnauthorizedError("Invalid X-User-Role header") from exc

    venue_id: int | None = None
    if x_user_venue_id is not None:
        try:
            venue_id = int(x_user_venue_id)
        except ValueError as exc:
            raise UnauthorizedError("Invalid X-User-Venue-ID header") from exc

    return IdentityContext(
        user_id=user_id,
        role=role,
        request_id=request_id,
        venue_id=venue_id,
    )


async def require_admin(
  identity: Annotated[IdentityContext, Depends(get_identity_context)],
) -> None:
  if identity.role != UserRole.ADMIN:
    raise ForbiddenError()


async def get_company_service(
  session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CompanyService:
  return CompanyService(session=session)


async def get_venue_service(
  session: Annotated[AsyncSession, Depends(get_db_session)],
) -> VenueService:
  return VenueService(session=session)


async def get_event_publisher(request: Request) -> EventPublisher:
  publisher = getattr(request.app.state, "event_publisher", None)
  if publisher is None:
    return NoopEventPublisher()
  return cast(EventPublisher, publisher)


async def get_payout_service(
  session: Annotated[AsyncSession, Depends(get_db_session)],
  event_publisher: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> PayoutService:
  return PayoutService(session=session, event_publisher=event_publisher)
