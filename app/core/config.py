import os
from typing import Dict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "RateShield Gateway"
    API_V1_PREFIX: str = "/api/v1"
    
    JWT_SECRET_KEY: str = "change-me-in-production-rateshield-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = "sqlite:///./app.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_BASIC: int = 60
    RATE_LIMIT_PREMIUM: int = 300
    RATE_LIMIT_ADMIN: int = 1000

    @property
    def rate_limits_by_tier(self) -> Dict[str, int]:
        return {
            "basic": self.RATE_LIMIT_BASIC,
            "premium": self.RATE_LIMIT_PREMIUM,
            "admin": self.RATE_LIMIT_ADMIN,
        }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Backwards compatibility re-exports if needed by any legacy imports
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REDIS_URL = settings.REDIS_URL
RATE_LIMIT_WINDOW_SECONDS = settings.RATE_LIMIT_WINDOW_SECONDS
RATE_LIMITS_BY_TIER = settings.rate_limits_by_tier
