from tortoise.fields.data import (BinaryField, BooleanField, CharField,
                                  DatetimeField, IntEnumField, IntField,
                                  JSONField, UUIDField)
from tortoise.fields.relational import (ForeignKeyField, ForeignKeyRelation,
                                        ReverseRelation)
from tortoise.models import Model

from ..helpers.constants import ContentChangeTypes
from .custom_fields import PathField


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
    is_admin = BooleanField(default=False)
    disabled = BooleanField(default=False)

    content_changes: ReverseRelation["ContentChange"]


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
    triggered_by: ForeignKeyRelation[User] = ForeignKeyField(
        "models.User",
        "content_changes",
        null=True
    )
    extra_meta = JSONField(null=True)


class FileShare(Model):
    """
    a file that was shared

        uuid: the primary key
        path: the filepath
        expires: when the link expires (or not)
        uses_left: how many uses are left (if has use limit)
    """
    uuid = UUIDField(pk=True)
    path = PathField()
    expires = DatetimeField(null=True)
    uses_left = IntField(null=True)
