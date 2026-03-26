from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.core_exceptions import ConflictError, ForbiddenError, NotFoundError
from src.events.publisher import EventPublisher, NoopEventPublisher
from src.events.schemas import DomainEvent, EventMetadata
from src.events.topics import PAYOUT_CREATED, PAYOUT_EXCHANGE, PAYOUT_PAID
from src.models.payout import Payout
from src.repositories.payout_repository import PayoutRepository
from src.repositories.venue_repository import VenueRepository
from src.schemas.common import IdentityContext, UserRole
from src.schemas.payout import PayoutCreate, PayoutListQuery, PayoutStatus, PayoutStatusUpdate


class PayoutService:
  def __init__(
    self,
    session: AsyncSession,
    *,
    event_publisher: EventPublisher | None = None,
  ) -> None:
    self.session = session
    self.repository = PayoutRepository(session)
    self.venue_repository = VenueRepository(session)
    self.event_publisher: EventPublisher
    if event_publisher is None:
      self.event_publisher = NoopEventPublisher()
    else:
      self.event_publisher = event_publisher

  async def list_payouts(
    self,
    *,
    venue_id: int,
    query: PayoutListQuery,
    identity: IdentityContext,
  ) -> tuple[list[Payout], int]:
    await self._check_venue_access(venue_id=venue_id, identity=identity, write_access=False)

    items = await self.repository.list_by_venue(
      venue_id=venue_id,
      status=query.status,
      limit=query.limit,
      offset=query.offset,
    )
    total = await self.repository.count_by_venue(venue_id=venue_id, status=query.status)
    return items, total

  async def create_payout(
    self,
    *,
    venue_id: int,
    payload: PayoutCreate,
    identity: IdentityContext,
  ) -> Payout:
    await self._check_venue_access(venue_id=venue_id, identity=identity, write_access=True)

    payout = await self.repository.create(
      {
        "venue_id": venue_id,
        "amount": payload.amount,
        "period_start": payload.period_start,
        "period_end": payload.period_end,
        "payment_details": payload.payment_details,
        "status": PayoutStatus.PENDING.value,
      }
    )
    await self.session.commit()

    event = DomainEvent(
      event_type=PAYOUT_CREATED,
      aggregate_id=str(payout.id),
      aggregate_type="Payout",
      payload={
        "payout_id": payout.id,
        "venue_id": payout.venue_id,
        "amount": str(payout.amount),
        "period_start": payout.period_start.isoformat(),
        "period_end": payout.period_end.isoformat(),
        "status": payout.status,
      },
      metadata=EventMetadata(
        correlation_id=identity.request_id,
        user_id=identity.user_id,
      ),
    )
    await self.event_publisher.publish(
      exchange=PAYOUT_EXCHANGE,
      routing_key=PAYOUT_CREATED,
      event=event,
    )

    return payout

  async def update_status(
    self,
    *,
    venue_id: int,
    payout_id: int,
    payload: PayoutStatusUpdate,
    identity: IdentityContext,
  ) -> Payout:
    if identity.role != UserRole.ADMIN:
      raise ForbiddenError()

    venue = await self.venue_repository.get_by_id(venue_id)
    if venue is None:
      raise NotFoundError("Venue not found")

    payout = await self.repository.get_by_id_for_venue(payout_id=payout_id, venue_id=venue_id)
    if payout is None:
      raise NotFoundError("Payout not found")

    if payout.status != PayoutStatus.PENDING.value:
      raise ConflictError("Only pending payouts can be updated")

    if payload.status == PayoutStatus.PAID:
      if venue.payout_balance < payout.amount:
        raise ConflictError("Insufficient payout balance")
      venue.payout_balance -= payout.amount
      payout.paid_at = datetime.now(timezone.utc)
    else:
      payout.paid_at = None

    payout.status = payload.status.value

    await self.session.flush()
    await self.session.refresh(payout)
    await self.session.commit()

    if payload.status == PayoutStatus.PAID:
      event = DomainEvent(
        event_type=PAYOUT_PAID,
        aggregate_id=str(payout.id),
        aggregate_type="Payout",
        payload={
          "payout_id": payout.id,
          "venue_id": payout.venue_id,
          "amount": str(payout.amount),
          "status": payout.status,
          "paid_at": payout.paid_at.isoformat() if payout.paid_at else None,
        },
        metadata=EventMetadata(
          correlation_id=identity.request_id,
          user_id=identity.user_id,
        ),
      )
      await self.event_publisher.publish(
        exchange=PAYOUT_EXCHANGE,
        routing_key=PAYOUT_PAID,
        event=event,
      )

    return payout

  async def _check_venue_access(
    self,
    *,
    venue_id: int,
    identity: IdentityContext,
    write_access: bool,
  ) -> None:
    venue = await self.venue_repository.get_by_id(venue_id)
    if venue is None:
      raise NotFoundError("Venue not found")

    if write_access:
      if identity.role != UserRole.ADMIN:
        raise ForbiddenError()
      return

    if identity.role == UserRole.ADMIN:
      return

    if identity.role != UserRole.STAFF:
      raise ForbiddenError()

    if identity.venue_id != venue_id:
      raise ForbiddenError("Staff can only access payouts for own venue")
