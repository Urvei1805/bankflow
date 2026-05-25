"""
BankFlow Analytics Service — Core Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    from pydantic import Field

    APP_NAME: str = "BankFlow Analytics Service"
    ENVIRONMENT: str = Field(default="development", alias="ENV")
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Database
    CUSTOM_DATABASE_URL: str | None = Field(default=None, alias="DATABASE_URL")
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "bankflow"
    POSTGRES_USER: str = "bankflow_user"
    POSTGRES_PASSWORD: str = "change_me_in_production"

    # Redis
    CUSTOM_REDIS_URL: str | None = Field(default=None, alias="REDIS_URL")
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    ANALYTICS_CACHE_TTL: int = 60

    # Service URLs & Auth
    AUTH_SERVICE_URL: str = "http://auth-service:8001"
    BANKING_API_URL: str = "http://banking-api-service:8002"
    ANALYTICS_SERVICE_URL: str = "http://analytics-service:8003"
    JWT_SECRET_KEY: str = "change-this-to-a-random-secret-in-production"
    JWT_PUBLIC_KEY_PATH: str = "/app/keys/public.pem"
    JWT_PRIVATE_KEY_PATH: str = "/app/keys/private.pem"
    API_KEY_SECRET: str = "change-this-api-key-secret-in-production"

    @property
    def database_url(self) -> str:
        if self.CUSTOM_DATABASE_URL:
            return self.CUSTOM_DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        if self.CUSTOM_REDIS_URL:
            return self.CUSTOM_REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/2"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
