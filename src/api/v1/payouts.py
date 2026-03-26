from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.api.deps import get_identity_context, get_payout_service
from src.schemas.common import IdentityContext, PaginatedResponse, PaginationMeta
from src.schemas.payout import PayoutCreate, PayoutListQuery, PayoutResponse
from src.services.payout_service import PayoutService

router = APIRouter(prefix="/venues/{venue_id}/payouts", tags=["Payouts"])


@router.get("", response_model=PaginatedResponse[PayoutResponse])
async def list_payouts(
    venue_id: int,
    service: Annotated[PayoutService, Depends(get_payout_service)],
    identity: Annotated[IdentityContext, Depends(get_identity_context)],
    query: Annotated[PayoutListQuery, Query()],
) -> PaginatedResponse[PayoutResponse]:
    items, total = await service.list_payouts(
        venue_id=venue_id,
        query=query,
        identity=identity,
    )
    return PaginatedResponse[PayoutResponse](
        items=[PayoutResponse.model_validate(item) for item in items],
        meta=PaginationMeta(limit=query.limit, offset=query.offset, total=total),
    )


@router.post("", response_model=PayoutResponse, status_code=status.HTTP_201_CREATED)
async def create_payout(
    venue_id: int,
    payload: PayoutCreate,
    service: Annotated[PayoutService, Depends(get_payout_service)],
    identity: Annotated[IdentityContext, Depends(get_identity_context)],
) -> PayoutResponse:
    payout = await service.create_payout(
        venue_id=venue_id,
        payload=payload,
        identity=identity,
    )
    return PayoutResponse.model_validate(payout)
