from fastapi import APIRouter
from src.api.v1 import api_v1_router
from src.api.routes.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(api_v1_router)

__all__ = ["api_router"]