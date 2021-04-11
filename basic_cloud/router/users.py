from fastapi import APIRouter, Depends

from ..database import models, schema
from ..helpers import auth

router = APIRouter()


@router.get("/me", response_model=schema.User)
async def get_me(user: models.User = Depends(auth.get_current_user)):
    return user
