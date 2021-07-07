from fastapi import APIRouter

from ..helpers.constants import CURRENT_VERSION, OLDEST_COMPATIBLE_VERSION
from ..helpers.schema import ApiVersion

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
