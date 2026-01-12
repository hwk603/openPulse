"""
Configuration management for OpenPulse platform
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "OpenPulse"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"

    # OpenDigger
    OPENDIGGER_API_URL: str = "https://oss.x-lab.info/open_digger"
    OPENDIGGER_TIMEOUT: int = 30

    # Apache IoTDB
    IOTDB_HOST: str = "localhost"
    IOTDB_PORT: int = 6667
    IOTDB_USER: str = "root"
    IOTDB_PASSWORD: str = "root"
    IOTDB_DATABASE: str = "root.openpulse"

    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "openpulse"
    POSTGRES_PASSWORD: str = "openpulse"
    POSTGRES_DB: str = "openpulse"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @property
    def celery_broker(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def celery_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    # Analysis Parameters
    CHURN_PREDICTION_WINDOW_DAYS: int = 90
    CHURN_PREDICTION_THRESHOLD: float = 0.7
    HEALTH_SCORE_WEIGHTS: dict = {
        "activity": 0.25,
        "diversity": 0.15,
        "response_time": 0.15,
        "code_quality": 0.15,
        "documentation": 0.15,
        "community_atmosphere": 0.15
    }

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/openpulse.log"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
