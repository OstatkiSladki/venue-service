from sqlalchemy.ext.asyncio import AsyncSession

from src.core_exceptions import ForbiddenError, NotFoundError
from src.models.venue import Venue
from src.repositories.venue_repository import VenueRepository
from src.schemas.common import IdentityContext, UserRole
from src.schemas.venue import VenueCreate, VenueListQuery, VenueUpdate


class VenueService:
  def __init__(self, session: AsyncSession) -> None:
    self.session = session
    self.repository = VenueRepository(session)

  async def list_venues(
    self,
    *,
    identity: IdentityContext,
    query: VenueListQuery,
  ) -> tuple[list[Venue], int]:
    if query.include_deleted and identity.role != UserRole.ADMIN:
      raise ForbiddenError()

    items = await self.repository.list_filtered(
      limit=query.limit,
      offset=query.offset,
      include_deleted=query.include_deleted,
      name=query.name,
      is_open=query.is_open,
      company_id=query.company_id,
      lat=query.lat,
      lon=query.lon,
      radius_km=query.radius,
    )
    total = await self.repository.count_filtered(
      include_deleted=query.include_deleted,
      name=query.name,
      is_open=query.is_open,
      company_id=query.company_id,
      lat=query.lat,
      lon=query.lon,
      radius_km=query.radius,
    )
    return items, total

  async def get_venue(self, *, venue_id: int, identity: IdentityContext) -> Venue:
    _ = identity
    venue = await self.repository.get_by_id(venue_id)
    if venue is None:
      raise NotFoundError("Venue not found")
    return venue

  async def create_venue(self, *, payload: VenueCreate, identity: IdentityContext) -> Venue:
    if identity.role not in {UserRole.ADMIN, UserRole.STAFF}:
      raise ForbiddenError()

    await self._validate_staff_company_scope(identity=identity, company_id=payload.company_id)

    data = payload.model_dump(exclude_none=True)
    if identity.role != UserRole.ADMIN:
      data.pop("commission_rate", None)

    venue = await self.repository.create(data)
    await self.session.commit()
    return venue

  async def update_venue(
    self,
    *,
    venue_id: int,
    payload: VenueUpdate,
    identity: IdentityContext,
  ) -> Venue:
    venue = await self.repository.get_by_id(venue_id)
    if venue is None:
      raise NotFoundError("Venue not found")

    if identity.role == UserRole.USER:
      raise ForbiddenError()

    if identity.role == UserRole.STAFF:
      await self._validate_staff_company_scope(identity=identity, company_id=venue.company_id)

    data = payload.model_dump(exclude_unset=True)
    if identity.role != UserRole.ADMIN and "commission_rate" in data:
      raise ForbiddenError("Only admin can update commission_rate")

    updated = await self.repository.update(venue, data)
    await self.session.commit()
    return updated

  async def soft_delete_venue(self, *, venue_id: int, identity: IdentityContext) -> None:
    if identity.role != UserRole.ADMIN:
      raise ForbiddenError()

    venue = await self.repository.get_by_id(venue_id)
    if venue is None:
      raise NotFoundError("Venue not found")

    await self.repository.soft_delete(venue)
    await self.session.commit()

  async def _validate_staff_company_scope(
    self,
    *,
    identity: IdentityContext,
    company_id: int | None,
  ) -> None:
    if identity.role != UserRole.STAFF:
      return

    if identity.venue_id is None:
      raise ForbiddenError("Staff user must have X-User-Venue-ID header")

    own_venue = await self.repository.get_by_id(identity.venue_id)
    if own_venue is None:
      raise ForbiddenError("Staff venue not found")

    if own_venue.company_id is None or company_id != own_venue.company_id:
      raise ForbiddenError("Staff can only manage venues inside own company")
