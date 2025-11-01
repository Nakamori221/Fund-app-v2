"""Configuration management for Fund IC Automation System"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application Settings"""

    # Application
    APP_NAME: str = "Fund IC Automation System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production

    # Database
    DATABASE_URL: str = "postgresql://fund_user:fund_dev_password@localhost:5432/fund_ic_dev"
    DATABASE_ECHO: bool = True

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # API
    API_V1_STR: str = "/api/v1"
    API_TITLE: str = "Fund IC Automation API"
    API_DESCRIPTION: str = "REST API for Fund IC Automation System"

    # Security
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Logging
    LOG_LEVEL: str = "INFO"

    # OpenAI
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"
    LLM_TEMPERATURE_EXTRACTION: float = 0.1
    LLM_TEMPERATURE_GENERATION: float = 0.3

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIRECTORY: str = "./uploads"

    # Retry Settings
    MAX_RETRIES: int = 3
    INITIAL_RETRY_DELAY: int = 2
    MAX_RETRY_DELAY: int = 30

    # Data Processing
    MAX_CONTENT_LENGTH: int = 10000
    DEFAULT_CONFIDENCE: float = 0.9
    CONFLICT_THRESHOLD_PCT: float = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
