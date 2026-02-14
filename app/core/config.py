from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    JWT_TTL_MINUTES: int = 1440

    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    STORAGE_ROOT: str = str(Path("storage").resolve())
    BIRTH_CERTS_DIR: str = "birth_certs"
    MAX_UPLOAD_MB: int = 10

    CORS_ORIGINS: str = "*"


settings = Settings()
