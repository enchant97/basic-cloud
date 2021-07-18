"""
tortoise fields that are missing
"""
from hashlib import sha256
from pathlib import Path
from typing import Any, Optional

from tortoise.fields import CharField

__all__ = (
    "Sha256Field",
)


class Sha256Field(CharField):
    """
    automatically hash the string when set
    """
    def __init__(self, **kwargs):
        super().__init__(64, **kwargs)

    def to_db_value(self, value: Any, _instance) -> Optional[str]:
        return None if value is None else sha256(str(value).encode()).hexdigest()
