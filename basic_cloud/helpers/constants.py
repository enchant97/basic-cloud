from enum import IntEnum, unique
from pathlib import Path

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

MODULE_PATH = Path(__file__).resolve(strict=True).parent.parent
TEMPLATES = Jinja2Templates(directory=MODULE_PATH / Path("templates"))
STATIC = StaticFiles(directory=MODULE_PATH / Path("static"))


@unique
class ContentChangeTypes(IntEnum):
    """
    enums responsible for marking
    how the content has changed

        OTHER_CHANGE: any change that doesn't
                      have a registered type
        CREATION: a file/directory was created
        DELETION: a file/directory was deleted
        DOWNLOAD: a file/directory was downloaded
    """
    OTHER_CHANGE = 0
    CREATION = 1
    DELETION = 2
    DOWNLOAD = 3
