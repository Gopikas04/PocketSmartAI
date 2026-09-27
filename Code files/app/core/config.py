from functools import lru_cache
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change-me"
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'pocketsmart.db'}"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    gemini_temperature: float = 0.35
    cors_origins: list[str] = ["http://127.0.0.1:8000", "http://localhost:8000"]
    session_max_age: int = 86400
    max_upload_mb: int = 8

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value):
        if isinstance(value, str):
            return [x.strip() for x in value.split(",") if x.strip()]
        return value

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
