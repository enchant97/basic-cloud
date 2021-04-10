from fastapi import FastAPI

from .router import html

app = FastAPI()
app.mount("/static", app, name="static")

app.include_router(html.router, tags=["html"])
