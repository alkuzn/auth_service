import uvicorn

from registration_service.config import Config

if __name__ == "__main__":
    uvicorn.run(**Config.uvicorn_settings)
