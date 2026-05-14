from __future__ import annotations

from decimal import Decimal, InvalidOperation

import grpc

from src.db.session import get_session_factory
from src.grpc.generated import venue_directory_pb2, venue_directory_pb2_grpc
from src.models.venue import Venue
from src.repositories.venue_repository import VenueRepository


def _to_string(value: Decimal | None) -> str:
  if value is None:
    return ""
  return str(value)


def _to_status(venue: Venue) -> str:
  return "deleted" if venue.deleted_at is not None else "active"


def _to_get_venue_response(venue: Venue) -> venue_directory_pb2.GetVenueByIdResponse:
  return venue_directory_pb2.GetVenueByIdResponse(
    venue_id=int(venue.id),
    name=str(venue.name),
    address=str(venue.address),
    is_open=bool(venue.is_open),
    commission_rate=_to_string(venue.commission_rate),
    status=_to_status(venue),
  )


class VenueDirectoryGrpcService(venue_directory_pb2_grpc.VenueDirectoryServiceServicer):
  async def GetVenueById(
    self,
    request: venue_directory_pb2.GetVenueByIdRequest,
    context: grpc.aio.ServicerContext,
  ) -> venue_directory_pb2.GetVenueByIdResponse:
    session_factory = get_session_factory()
    async with session_factory() as session:
      venue = await VenueRepository(session).get_by_id(int(request.venue_id), include_deleted=True)
      if venue is None:
        await context.abort(grpc.StatusCode.NOT_FOUND, "Venue not found")
      return _to_get_venue_response(venue)

  async def GetVenueCoordinates(
    self,
    request: venue_directory_pb2.GetVenueCoordinatesRequest,
    context: grpc.aio.ServicerContext,
  ) -> venue_directory_pb2.GetVenueCoordinatesResponse:
    session_factory = get_session_factory()
    async with session_factory() as session:
      venue = await VenueRepository(session).get_by_id(int(request.venue_id), include_deleted=True)
      if venue is None:
        await context.abort(grpc.StatusCode.NOT_FOUND, "Venue not found")
      return venue_directory_pb2.GetVenueCoordinatesResponse(
        latitude=_to_string(venue.latitude),
        longitude=_to_string(venue.longitude),
      )

  async def UpdatePayoutBalance(
    self,
    request: venue_directory_pb2.UpdatePayoutBalanceRequest,
    context: grpc.aio.ServicerContext,
  ) -> venue_directory_pb2.UpdatePayoutBalanceResponse:
    if not request.operation_id.strip():
      await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "operation_id is required")

    try:
      amount = Decimal(request.amount)
    except InvalidOperation:
      await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "amount must be a decimal string")

    session_factory = get_session_factory()
    async with session_factory() as session:
      repository = VenueRepository(session)
      venue = await repository.get_by_id_for_update(int(request.venue_id))
      if venue is None:
        await context.abort(grpc.StatusCode.NOT_FOUND, "Venue not found")

      venue.payout_balance += amount
      await session.commit()
      await session.refresh(venue)

      return venue_directory_pb2.UpdatePayoutBalanceResponse(
        success=True,
        new_balance=_to_string(venue.payout_balance),
      )

  async def CheckVenueExists(
    self,
    request: venue_directory_pb2.CheckVenueExistsRequest,
    context: grpc.aio.ServicerContext,
  ) -> venue_directory_pb2.CheckVenueExistsResponse:
    session_factory = get_session_factory()
    async with session_factory() as session:
      venue = await VenueRepository(session).get_by_id(int(request.venue_id))
      return venue_directory_pb2.CheckVenueExistsResponse(exists=venue is not None)

  async def ValidateVenue(
    self,
    request: venue_directory_pb2.ValidateVenueRequest,
    context: grpc.aio.ServicerContext,
  ) -> venue_directory_pb2.ValidateVenueResponse:
    session_factory = get_session_factory()
    async with session_factory() as session:
      venue = await VenueRepository(session).get_by_id(int(request.venue_id), include_deleted=True)
      if venue is None:
        return venue_directory_pb2.ValidateVenueResponse(is_valid=False, status="")
      return venue_directory_pb2.ValidateVenueResponse(
        is_valid=_to_status(venue) == "active",
        status=_to_status(venue),
      )

  async def GetVenueInfo(
    self,
    request: venue_directory_pb2.GetVenueInfoRequest,
    context: grpc.aio.ServicerContext,
  ) -> venue_directory_pb2.GetVenueInfoResponse:
    session_factory = get_session_factory()
    async with session_factory() as session:
      venue = await VenueRepository(session).get_by_id(int(request.venue_id), include_deleted=True)
      if venue is None:
        await context.abort(grpc.StatusCode.NOT_FOUND, "Venue not found")
      return venue_directory_pb2.GetVenueInfoResponse(
        venue_id=int(venue.id),
        name=str(venue.name),
        address=str(venue.address),
        is_open=bool(venue.is_open),
        commission_rate=_to_string(venue.commission_rate),
        status=_to_status(venue),
        accepts_promo_codes=False,
        allowed_payment_methods=[],
      )
