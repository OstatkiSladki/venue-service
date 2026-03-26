from fastapi import APIRouter

from src.api.v1.companies import router as companies_router
from src.api.v1.payouts import router as payouts_router
from src.api.v1.venues import router as venues_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(companies_router)
api_v1_router.include_router(venues_router)
api_v1_router.include_router(payouts_router)
