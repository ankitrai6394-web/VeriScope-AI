"""Application Configuration Module."""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "VeriScope AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./veriscope.db"
    DATABASE_SYNC_URL: str = "sqlite:///./veriscope.db"

    # LLM Settings
    LLM_PROVIDER: str = "gemini"  # "gemini", "openai", "mock"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-3.5-flash-lite"
    LLM_TEMPERATURE: float = 0.2
    LLM_TIMEOUT_SECONDS: int = 30

    # Search Settings
    SEARCH_PROVIDER: str = "tavily"  # "tavily", "mock"
    SEARCH_API_KEY: Optional[str] = None
    MAX_SEARCH_RESULTS_PER_QUERY: int = 5
    SEARCH_TIMEOUT_SECONDS: int = 20

    # Security & Limits
    MAX_RESEARCH_QUERY_LENGTH: int = 500
    MAX_CONCURRENT_AGENT_TASKS: int = 4
    HTTP_REQUEST_TIMEOUT_SECONDS: int = 25
    MAX_EXTERNAL_PAGE_DOWNLOAD_BYTES: int = 1048576  # 1 MB
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
