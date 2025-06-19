from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from nonebot import logger
from nonebot_plugin_htmlrender import template_to_pic as t2p

from ..vrchat import ApiClient, LimitedUserModel, UserModel


async def draw_world_card_overview(
    users: List[LimitedUserModel],
    group: bool = True,
    client: Optional[ApiClient] = None,
    title: str = "好友列表",
) -> bytes: ...
