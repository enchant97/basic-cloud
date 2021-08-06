from tortoise.fields.data import (BinaryField, BooleanField, CharField,
                                  DatetimeField, IntEnumField, IntField,
                                  JSONField, UUIDField)
from tortoise.fields.relational import (ForeignKeyField, ForeignKeyRelation,
                                        ReverseRelation)
from tortoise.models import Model

from ..helpers.constants import ContentChangeTypes
from .custom_fields import PathField, Sha256Field


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


class FakePath(Model):
    """
    store a 'fake' path

        path_hash: the unique hash of the path
        path: the actual path
        is_dir: whether path is a directory
    """
    path_hash = Sha256Field(unique=True)
    path = PathField()
    is_dir = BooleanField()

    content_changes: ReverseRelation["ContentChange"]
    shares: ReverseRelation["Share"]


class ContentChange(Model):
    """
    marks each change to the shares

        fake_path: the path that it relates to
        created_at: datetime stamp when the change occured
        type_enum: the type of change that occured
        extra_meta: any extra meta to store
    """
    fake_path: ForeignKeyRelation[FakePath] = ForeignKeyField(
        "models.FakePath",
        "content_changes",
    )
    created_at = DatetimeField(auto_now_add=True)
    type_enum = IntEnumField(ContentChangeTypes)
    triggered_by: ForeignKeyRelation[User] = ForeignKeyField(
        "models.User",
        "content_changes",
        null=True
    )
    extra_meta = JSONField(null=True)


class Share(Model):
    """
    a path that was shared

        uuid: the primary key
        fake_path: the path that it relates to
        expires: when the link expires (or not)
        uses_left: how many uses are left (if has use limit)
    """
    uuid = UUIDField(pk=True)
    fake_path: ForeignKeyRelation[FakePath] = ForeignKeyField(
        "models.FakePath",
        "shares",
    )
    expires = DatetimeField(null=True)
    uses_left = IntField(null=True)
