from fastapi import FastAPI

from src.utils import cors_setup, lifespan
from src.api import api_router
from src.config.logging import configure_logging
from src.config.settings import get_settings
from src.middleware import register_exception_handlers, RequestContextMiddleware



def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
    cors_setup(app)
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)

    app.include_router(api_router)

    return app


app = create_app()