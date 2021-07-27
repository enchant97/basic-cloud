from fastapi import APIRouter, Depends

from ..config import get_settings
from ..database import models
from ..helpers.auth import get_current_admin_user
from ..helpers.constants import CURRENT_VERSION, OLDEST_COMPATIBLE_VERSION
from ..helpers.paths import (calculate_directory_file_count,
                             calculate_directory_size)
from ..helpers.schema import ApiVersion, DirectoryStats, RootStats

router = APIRouter()


@router.get(
    "/version",
    response_model=ApiVersion,
    description="gets the current api version")
async def api_version():
    return ApiVersion(
        version=CURRENT_VERSION,
        oldest_compatible=OLDEST_COMPATIBLE_VERSION
    )


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
