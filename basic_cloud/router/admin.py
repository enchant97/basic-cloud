from pathlib import Path

from fastapi import APIRouter, Depends

from ..config import get_settings
from ..database import models
from ..helpers.auth import get_current_admin_user
from ..helpers.paths import calculate_directory_size, calculate_directory_file_count
from ..helpers.schema import DirectoryStats, RootStats

router = APIRouter()


@router.get(
    "/stats/roots",
    response_model=RootStats,
    description="get the directory root stats")
async def root_stats(curr_user: models.User = Depends(get_current_admin_user)):
    share_path = get_settings().SHARED_PATH
    home_path = get_settings().HOMES_PATH
    return RootStats(
        shared=DirectoryStats(
            path=share_path.name,
            bytes_size=calculate_directory_size(share_path),
            file_count=calculate_directory_file_count(share_path),
        ),
        homes=DirectoryStats(
            path=home_path.name,
            bytes_size=calculate_directory_size(home_path),
            file_count=calculate_directory_file_count(home_path),
        ),
    )
