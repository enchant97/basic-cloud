from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..config import get_settings
from ..database import schema
from ..helpers.auth import authenticate_user, create_access_token

router = APIRouter()


@router.post("/token", response_model=schema.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
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
