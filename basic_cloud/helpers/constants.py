from enum import IntEnum, unique
from pathlib import Path

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

MODULE_PATH = Path(__file__).resolve(strict=True).parent.parent
TEMPLATES = Jinja2Templates(directory=MODULE_PATH / Path("templates"))
STATIC = StaticFiles(directory=MODULE_PATH / Path("static"))

# the current version
CURRENT_VERSION = "0.3.0"
# the oldest compatible version
# that will work with current version
OLDEST_COMPATIBLE_VERSION = "0.1.0"


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
        SHARED: a file/directory was shared
    """
    OTHER_CHANGE = 0
    CREATION = 1
    DELETION = 2
    DOWNLOAD = 3
    SHARED = 4


@unique
class WebsocketMessageTypeSend(IntEnum):
    """
    enums responsible for marking
    what payload has been sent
    in a message from the server

        WATCHDOG_UPDATE: change from the file/directory watchdog
    """
    WATCHDOG_UPDATE = 1


@unique
class WebsocketMessageTypeReceive(IntEnum):
    """
    enums responsible for marking
    what payload has been sent
    in a message from the client

        DIRECTORY_CHANGE: client has changed directory
    """
    DIRECTORY_CHANGE = 1
