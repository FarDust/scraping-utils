from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    """Database configuration."""

    url: str = "sqlite:///./scraped_data.db"


class FirecrawlConfig(BaseModel):
    """Firecrawl configuration."""

    base_url: str = "http://localhost:3002/"
    api_key: str | None = None


class Settings(BaseSettings):
    """Load settings from .env file."""

    db: DatabaseConfig = DatabaseConfig()
    firecrawl: FirecrawlConfig = FirecrawlConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )
