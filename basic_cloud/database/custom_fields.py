"""
tortoise fields that are missing
"""
from pathlib import Path
from typing import Any, Optional

from tortoise.fields import BinaryField

__all__ = (
    "PathField",
)


class PathField(BinaryField):
    """
    Path Field

    This field can store a pathlib.Path value
    """
    def to_db_value(self, value: Any, _instance: "Union[Type[Model], Model]") -> Optional[str]:
        return value and str(value).encode()

    def to_python_value(self, value: Any) -> Optional[Path]:
        if value is None or isinstance(value, Path):
            return value
        return Path(value.decode())
