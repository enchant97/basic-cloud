from tortoise.fields.data import (BinaryField, BooleanField, CharField,
                                  DatetimeField, IntEnumField, JSONField,
                                  UUIDField)
from tortoise.models import Model

from ..helpers.constants import ContentChangeTypes


class ModifyMixin:
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)


class User(Model, ModifyMixin):
    """
    information about a user
    """
    uuid = UUIDField(pk=True)
    username = CharField(25, unique=True)
    hashed_password = BinaryField()
    disabled = BooleanField(default=False)


class ContentChange(Model):
    """
    marks each change to the shares

        created_at: datetime stamp when the change occured
        path_hash: the path hashed (allows for different path lengths)
        type_enum: the type of change that occured
        is_dir: whether the path is a directory
        extra_meta: any extra meta to store
    """
    created_at = DatetimeField(auto_now_add=True)
    path_hash = BinaryField()
    type_enum = IntEnumField(ContentChangeTypes)
    is_dir = BooleanField()
    extra_meta = JSONField(null=True)
