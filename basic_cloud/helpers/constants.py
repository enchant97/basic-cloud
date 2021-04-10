from pathlib import Path

from fastapi.templating import Jinja2Templates

MODULE_PATH = Path(__file__).resolve(strict=True).parent.parent
TEMPLATES = Jinja2Templates(directory=MODULE_PATH / Path("templates"))
