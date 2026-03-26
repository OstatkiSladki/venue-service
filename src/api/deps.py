from typing import Annotated
from typing import cast

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core_exceptions import ForbiddenError, UnauthorizedError
from src.db.session import get_db_session
from src.schemas.common import IdentityContext, UserRole
from src.services.company_service import CompanyService
from src.services.payout_service import PayoutService
from src.services.venue_service import VenueService


async def get_identity_context(
    request: Request,
) -> IdentityContext:
    identity = getattr(request.state, "identity", None)
    if identity is None:
        raise UnauthorizedError("Identity context is missing")
    return cast(IdentityContext, identity)


async def require_admin(identity: Annotated[IdentityContext, Depends(get_identity_context)]) -> None:
    if identity.role != UserRole.ADMIN:
        raise ForbiddenError()


async def get_company_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> CompanyService:
    return CompanyService(session=session)


async def get_venue_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> VenueService:
    return VenueService(session=session)


async def get_payout_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> PayoutService:
    return PayoutService(session=session)
