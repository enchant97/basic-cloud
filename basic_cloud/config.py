from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    DATA_PATH: Path = Path("data")
    DB_URI: str = "sqlite://app_data.db"

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
