from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.api.deps import get_identity_context, get_optional_identity_context, get_venue_service
from src.schemas.common import IdentityContext, PaginatedResponse, PaginationMeta
from src.schemas.venue import VenueCreate, VenueListQuery, VenueResponse, VenueUpdate
from src.services.venue_service import VenueService

router = APIRouter(prefix="/venues", tags=["Venues"])


@router.get("", response_model=PaginatedResponse[VenueResponse])
async def list_venues(
  service: Annotated[VenueService, Depends(get_venue_service)],
  identity: Annotated[IdentityContext | None, Depends(get_optional_identity_context)],
  query: Annotated[VenueListQuery, Query()],
) -> PaginatedResponse[VenueResponse]:
  items, total = await service.list_venues(
    identity=identity,
    query=query,
  )
  return PaginatedResponse[VenueResponse](
    items=[VenueResponse.model_validate(item) for item in items],
    meta=PaginationMeta(limit=query.limit, offset=query.offset, total=total),
  )


@router.post("", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
async def create_venue(
  payload: VenueCreate,
  service: Annotated[VenueService, Depends(get_venue_service)],
  identity: Annotated[IdentityContext, Depends(get_identity_context)],
) -> VenueResponse:
  venue = await service.create_venue(payload=payload, identity=identity)
  return VenueResponse.model_validate(venue)


@router.get("/{venue_id}", response_model=VenueResponse)
async def get_venue(
  venue_id: int,
  service: Annotated[VenueService, Depends(get_venue_service)],
  identity: Annotated[IdentityContext | None, Depends(get_optional_identity_context)],
) -> VenueResponse:
  venue = await service.get_venue(venue_id=venue_id, identity=identity)
  return VenueResponse.model_validate(venue)


@router.patch("/{venue_id}", response_model=VenueResponse)
async def patch_venue(
  venue_id: int,
  payload: VenueUpdate,
  service: Annotated[VenueService, Depends(get_venue_service)],
  identity: Annotated[IdentityContext, Depends(get_identity_context)],
) -> VenueResponse:
  venue = await service.update_venue(venue_id=venue_id, payload=payload, identity=identity)
  return VenueResponse.model_validate(venue)


@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue(
  venue_id: int,
  service: Annotated[VenueService, Depends(get_venue_service)],
  identity: Annotated[IdentityContext, Depends(get_identity_context)],
) -> None:
  await service.soft_delete_venue(venue_id=venue_id, identity=identity)
