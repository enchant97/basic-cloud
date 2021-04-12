import uvicorn

from .config import get_settings
from .main import app

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
