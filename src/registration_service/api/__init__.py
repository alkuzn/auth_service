from contextlib import asynccontextmanager

from fastapi import FastAPI

from registration_service.config import Config


@asynccontextmanager
async def life(app: FastAPI):
    yield


app = FastAPI(
    title="Registration service",
    lifespan=life,
    docs_url=Config.docs_url,
    redoc_url=Config.redoc_url,
    openapi_url=Config.openapi_url,
)
