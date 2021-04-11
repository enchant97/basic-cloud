from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from .config import get_settings
from .database import models
from .helpers.constants import STATIC
from .router import auth, folder, html, users

app = FastAPI()
app.mount("/static", STATIC, name="static")

app.include_router(html.router, tags=["html"])
app.include_router(auth.router)
app.include_router(users.router, prefix="/api/users")
app.include_router(folder.router, prefix="/api/directory")


@app.on_event("startup")
async def do_startup():
    # database setup
    register_tortoise(
        app,
        db_url=get_settings().DB_URI,
        modules={"models": [models]},
        generate_schemas=True,
        )
