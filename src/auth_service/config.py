from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    db_host: str = Field(env="DB_HOST")
    db_port: int = Field(env="DB_PORT")
    db_name: str = Field(env="DB_NAME")
    db_user: str = Field(env="DB_USER")
    db_password: str = Field(env="DB_PASSWORD")

    db_driver_async: str = Field(default="postgresql+asyncpg")
    db_driver_sync: str = Field(default="postgresql+psycopg")

    docs_url: str | None = Field(env="DOCS_URL", default=None)
    redoc_url: str | None = Field(env="REDOC_URL", default=None)
    openapi_url: str | None = Field(env="OPENAPI_URL", default=None)
    app_host: str = Field(env="APP_HOST", default="localhost")
    app_port: int = Field(env="APP_PORT", default=8000)

    def __db_url_(self, driver):
        return f"{driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def uvicorn_settings(self) -> dict:
        return {
            "app": "registration_service:app",
            "reload": True,
            "host": self.app_host,
            "port": self.app_port,
        }

    @property
    def db_asyncurl(self) -> str:
        return self._Settings__db_url_(self.db_driver_sync)

    @property
    def db_syncurl(self) -> str:
        return self._Settings__db_url_(self.db_driver_async)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
