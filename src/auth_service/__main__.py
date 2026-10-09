import uvicorn

from auth_service.config import settings

if __name__ == "__main__":
    uvicorn.run(
        host=settings.app.host, port=settings.app.port, **settings.uvicorn.model_dump()
    )
