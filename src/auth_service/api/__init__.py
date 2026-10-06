from contextlib import asynccontextmanager

from fastapi import FastAPI
from auth_service.api.func import CodeCarrier
from auth_service.config import settings


@asynccontextmanager
async def life(app: FastAPI):
    yield


app = FastAPI(
    title="Auth service",
    lifespan=life,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
)
