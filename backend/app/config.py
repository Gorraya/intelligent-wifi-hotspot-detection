"""
Application configuration using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Application
    app_name: str = "Intelligent Wi-Fi Hotspot Detection"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@db:5432/hotspot_detection",
        description="Async database URL"
    )
    database_url_sync: str = Field(
        default="postgresql://postgres:postgres@db:5432/hotspot_detection",
        description="Sync database URL for Alembic"
    )

    # Security
    secret_key: str = Field(default="CHANGE-THIS-TO-A-VERY-LONG-RANDOM-SECRET-KEY-IN-PRODUCTION")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]

    # Agent
    agent_ingest_token: Optional[str] = Field(default=None, description="Optional shared secret for agent")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
