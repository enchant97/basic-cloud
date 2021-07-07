from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from .config import get_settings
from .database import models
from .helpers.constants import STATIC
from .router import admin, auth, file, folder, html, other, users

tags_metadata = (
    {
        "name": "token",
        "description": "operations with user authentication tokens"
    },
    {
        "name": "other",
        "description": "operations that don't fit anywhere else"
    },
    {
        "name": "users",
        "description": "operations with users"
    },
    {
        "name": "directories",
        "description": "operations with directories"
    },
    {
        "name": "files",
        "description": "operations with files"
    },
    {
        "name": "admin",
        "description": "operations for admins"
    },
    {
        "name": "html",
        "description": "html pages to view"
    },
)

app = FastAPI(openapi_tags=tags_metadata)
app.mount("/static", STATIC, name="static")

app.include_router(html.router, tags=["html"])
app.include_router(auth.router, tags=["token"])
app.include_router(other.router, prefix="/api", tags=["other"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(folder.router, prefix="/api/directory", tags=["directories"])
app.include_router(file.router, prefix="/api/file", tags=["files"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.on_event("startup")
async def do_startup():
    # database setup
    register_tortoise(
        app,
        db_url=get_settings().DB_URI,
        modules={"models": [models]},
        generate_schemas=True,
        )
