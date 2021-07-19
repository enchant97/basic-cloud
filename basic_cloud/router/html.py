from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from ..helpers.constants import TEMPLATES

router = APIRouter(
    default_response_class=HTMLResponse,
    )


@router.get("/")
async def get_home(request: Request):
    return TEMPLATES.TemplateResponse("home.html", {
        'request': request,
    })
