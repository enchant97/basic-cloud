from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    SHARED_PATH: Path = Path("data/shared")
    HOMES_PATH: Path = Path("data/homes")
    DB_URI: str = "sqlite://app_data.db"
    SECRET_KEY: str
    SIGNUPS_ALLOWED: bool = True

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    HASH_ALGORITHM: str = "HS256"

    LOG_LEVEL: str = "WARNING"

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        secrets_dir = "/run/secrets"
        case_sensitive = True


@lru_cache()
def get_settings():
    """
    returns the Settings obj
    """
    return Settings()
