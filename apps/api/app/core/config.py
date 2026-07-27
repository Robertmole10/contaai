from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://redis:6379/0"

    minio_endpoint: str = "minio:9000"
    minio_secure: bool = False
    minio_bucket: str = "contaai-documents"
    minio_root_user: str
    minio_root_password: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    cookie_secure: bool = False
    session_secret: str

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"

    frontend_url: str = "http://localhost:3001/dashboard"
    frontend_origin: str = "http://localhost:3001"

    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:3001"
        "https://app-conta.bmobile.ro",
    ]

    model_config = SettingsConfigDict(case_sensitive=False)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [
                origin.strip()
                for origin in value.split(",")
                if origin.strip()
            ]
        return value

    @field_validator(
        "google_redirect_uri",
        "frontend_url",
        mode="before",
    )
    @classmethod
    def strip_url(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().rstrip("/")
        return value


settings = Settings()


VERSION_FILE = Path("/app/VERSION")


def get_app_version() -> str:
    try:
        return VERSION_FILE.read_text().strip()
    except Exception:
        return "dev"