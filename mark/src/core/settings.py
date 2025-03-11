import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):  # type: ignore
    PROJECT_NAME: str = "mark"
    APP_RELOAD: bool = True
    LOG_LEVEL: str = "INFO"

    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5442
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "mark"
    POSTGRES_DB_ECHO: bool = True

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @property
    def dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()
