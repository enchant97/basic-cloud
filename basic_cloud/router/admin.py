from fastapi import APIRouter, Depends

from ..config import get_settings
from ..database import models
from ..helpers.auth import get_current_admin_user
from ..helpers.paths import calculate_directory_size
from ..helpers.schema import RootStats

router = APIRouter()


@router.get(
    "/stats/roots",
    response_model=RootStats,
    description="get the directory root stats")
async def root_stats(curr_user: models.User = Depends(get_current_admin_user)):
    return RootStats(
        shared_size=calculate_directory_size(get_settings().SHARED_PATH),
        homes_size=calculate_directory_size(get_settings().HOMES_PATH)
    )
