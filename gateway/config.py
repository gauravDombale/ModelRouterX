from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ModelRouterX"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://mrx:mrx@localhost:5432/mrx"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    google_api_key: str | None = None
    groq_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    langfuse_secret_key: str | None = None
    langfuse_public_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"

    cache_ttl_seconds: int = 3600
    semantic_cache_threshold: float = 0.92
    request_timeout_seconds: float = 60.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

