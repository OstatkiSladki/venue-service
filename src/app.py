from fastapi import FastAPI

from src.utils import cors_setup, lifespan
from src.api import api_router
from src.config import configure_logging, get_settings
from src.middleware import (
  GatewayAuthMiddleware,
  RequestContextMiddleware,
  register_exception_handlers,
)


def create_app() -> FastAPI:
  settings = get_settings()
  configure_logging(settings)

  app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
  cors_setup(app)
  app.add_middleware(GatewayAuthMiddleware)
  app.add_middleware(RequestContextMiddleware)

  register_exception_handlers(app)

  app.include_router(api_router)

  return app


app = create_app()
