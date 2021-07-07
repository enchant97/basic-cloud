from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..config import get_settings
from ..database import crud, schema
from ..helpers.auth import (authenticate_user, create_access_token,
                            get_password_hash)
from ..helpers.paths import create_user_home_dir

router = APIRouter()


@router.post("/token", response_model=schema.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    # create default admin user
    admin_uname = get_settings().DEFAULT_ADMIN_UNAME
    if form_data.username == admin_uname:
        await crud.create_default_admin(
            admin_uname,
            get_password_hash(admin_uname)
        )
        create_user_home_dir(admin_uname, get_settings().HOMES_PATH)

    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_expires = timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.uuid.hex},
        expires_delta=token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
