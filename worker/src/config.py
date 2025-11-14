"""
Worker configuration
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ClickHouse
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 9000
    CLICKHOUSE_HTTP_PORT: int = 8123
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""
    CLICKHOUSE_DATABASE: str = "trading"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Application
    LOG_LEVEL: str = "INFO"
    COLLECTION_INTERVAL_SECONDS: int = 10
    BATCH_INSERT_SIZE: int = 1000

    # Exchange API Keys (optional)
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""
    OKX_API_KEY: str = ""
    OKX_API_SECRET: str = ""
    OKX_PASSPHRASE: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
