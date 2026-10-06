import uvicorn

from registration_service.config import settings

if __name__ == "__main__":
    uvicorn.run(**settings.uvicorn_settings)
