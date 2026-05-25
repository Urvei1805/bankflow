"""
BankFlow Auth Service — Core Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ---- App ----
    APP_NAME: str = "BankFlow Auth Service"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # ---- Database ----
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "bankflow"
    POSTGRES_USER: str = "bankflow_user"
    POSTGRES_PASSWORD: str = "change_me_in_production"

    # ---- Redis ----
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # ---- JWT ----
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = "change-this-to-a-random-secret-in-production"
    JWT_PRIVATE_KEY_PATH: str = "/app/keys/private.pem"
    JWT_PUBLIC_KEY_PATH: str = "/app/keys/public.pem"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def jwt_private_key(self) -> str | None:
        """Load RSA private key from file if available."""
        path = self.JWT_PRIVATE_KEY_PATH
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read()
        return None

    @property
    def jwt_public_key(self) -> str | None:
        """Load RSA public key from file if available."""
        path = self.JWT_PUBLIC_KEY_PATH
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read()
        return None

    @property
    def effective_jwt_algorithm(self) -> str:
        """Use RS256 if RSA keys exist, fallback to HS256."""
        if self.jwt_private_key:
            return "RS256"
        return "HS256"

    @property
    def jwt_encode_key(self) -> str:
        """Key used to encode (sign) JWTs."""
        if self.jwt_private_key:
            return self.jwt_private_key
        return self.JWT_SECRET_KEY

    @property
    def jwt_decode_key(self) -> str:
        """Key used to decode (verify) JWTs."""
        if self.jwt_public_key:
            return self.jwt_public_key
        return self.JWT_SECRET_KEY

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
