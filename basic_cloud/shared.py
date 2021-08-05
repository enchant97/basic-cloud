from pathlib import Path

from .config import get_settings
from .database.crud import create_content_change
from .database.models import User
from .helpers.constants import ContentChangeTypes
from .helpers.websocket import dispatch_content_change


async def content_changed(
        path: Path,
        change_type: ContentChangeTypes,
        is_dir: bool,
        triggered_by: User):
    # log change to database if enabled
    if get_settings().HISTORY_LOG:
        await create_content_change(
            path,
            change_type,
            is_dir,
            triggered_by,
        )
    # notify any listening websockets
    await dispatch_content_change(path, change_type)
