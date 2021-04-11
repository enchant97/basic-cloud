from tortoise.fields.data import (BinaryField, BooleanField, CharField,
                                  DatetimeField, UUIDField)
from tortoise.models import Model


class ModifyMixin:
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)


class User(Model, ModifyMixin):
    uuid = UUIDField(pk=True)
    username = CharField(25, unique=True)
    hashed_password = BinaryField()
    disabled = BooleanField(default=False)
