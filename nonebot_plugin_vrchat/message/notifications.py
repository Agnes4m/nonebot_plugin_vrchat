from datetime import datetime, timezone
from pathlib import Path
from typing import List

from loguru import logger
from nonebot_plugin_htmlrender import template_to_pic as t2p
from vrchatapi import Notification

from .utils import td_format as td_fmt


async def draw_notification_card(
    ntfs: List[Notification],
    # client: Optional[ApiClient] = None,
):
    templates = []
    for index, ntf in enumerate(ntfs):
        time_now = datetime.now(timezone.utc)
        delta = time_now - ntf.created_at
        td = td_fmt(delta)
        logger.debug(ntf.type)
        templates.append(
            {
                "type": ntf.type,
                # 读取头像太慢，用默认头像
                # "avatar": await id_to_avatar(client,ntf.sender_user_id),
                "avatar": "default.png",
                "td": td[:-2],
                "message": ntf.message,
                "sender_username": ntf.sender_username,
                "index": index + 1,
            },
        )
    # 渲染图片
    logger.info(templates)
    return await t2p(
        template_path=str(Path(__file__).parent / "templates"),
        template_name="ntf.html",
        templates={"notifications": templates},
    )
