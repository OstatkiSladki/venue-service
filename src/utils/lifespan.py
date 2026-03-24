from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from fastapi import FastAPI

from src.db.session import close_engine

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    finally:
        await close_engine()