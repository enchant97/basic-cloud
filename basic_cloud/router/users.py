from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.exceptions import IntegrityError

from ..config import get_settings
from ..database import crud, models, schema
from ..helpers import auth
from ..helpers.auth import get_password_hash
from ..helpers.paths import create_user_home_dir

router = APIRouter()


@router.post("", response_model=schema.User)
async def create_account(
        new_user: schema.UserCreate):
    try:
        if not get_settings().SIGNUPS_ALLOWED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="signups are disabled",
            )
        pass_hash = get_password_hash(new_user.password)
        create_user_home_dir(new_user.username, get_settings().HOMES_PATH)
        return await crud.create_user(new_user.username, pass_hash)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already taken",
        ) from None


@router.get("/me", response_model=schema.User)
async def get_me(user: models.User = Depends(auth.get_current_user)):
    return user
