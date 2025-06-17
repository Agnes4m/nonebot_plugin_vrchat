from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from nonebot import logger
from nonebot_plugin_htmlrender import template_to_pic

from ..vrchat import ApiClient, LimitedUserModel
from .utils import (
    OFFLINE_STATUSES,
    STATUS_COLORS,
    STATUS_DESC_MAP,
    TRUST_COLORS,
    format_location,
    td_format,
)


async def draw_user_card_overview(
    users: List[LimitedUserModel],
    group: bool = True,
    client: Optional[ApiClient] = None,
    title: str = "好友列表",
) -> bytes:
    time_now = datetime.now(timezone.utc)
    raw_user_dict: Dict[str, List[dict]] = {}
    logger.debug(users)
    for user in users:
        loc = ""
        # content = user.status_description or STATUS_DESC_MAP[user.status]
        content = user.status_description
        if user.status in OFFLINE_STATUSES:
            logger.debug(f"user: {user.status}")
            if user.last_login:
                delta = time_now - user.last_login
                content = f"{content}\n{td_format(delta)}"
        elif user.status != "webonline" and user.location:
            loc = await format_location(client, user.location)
            content = f"{content}\n{loc}"

        user.location = content
        effective_status = user.status
        if user.status == "unknown" and user.original_status == "offline":
            effective_status = "offline"
        raw_user_dict.setdefault(effective_status, []).append(
            {
                "location": user.location,
                "original_status": user.original_status,
                "status_description": user.status_description,
                "display_name": user.display_name,
                "current_avatar_thumbnail_image_url": user.current_avatar_thumbnail_image_url,
                "trust": user.trust,
            },
        )

    # 按 STATUS_DESC_MAP 顺序排序
    if group:
        user_dict = {k: raw_user_dict[k] for k in STATUS_DESC_MAP if k in raw_user_dict}
    else:
        user_dict = {"unknown": [x for y in raw_user_dict.values() for x in y]}
    logger.debug(f"User dict: {user_dict}")
    # 按信任等级排序
    trust_keys = list(TRUST_COLORS.keys())
    for li in user_dict.values():
        li.sort(key=lambda x: trust_keys.index(x["trust"]), reverse=True)

    logger.debug(f"Draw user card overview for {len(users)} users")
    return await template_to_pic(
        template_path=str(Path(__file__).parent / "templates"),
        template_name="friend_list.html",
        templates={
            "user_dict": user_dict,
            "status_desc_map": STATUS_DESC_MAP,
            "status_colors": STATUS_COLORS,
            "title": title,
        },
    )


async def draw_user_profile_card(user: LimitedUserModel) -> bytes:
    if hasattr(user, "model_dump"):
        user_dict = user.model_dump()
    elif hasattr(user, "__dict__"):
        user_dict = user.__dict__
    else:
        user_dict = user
    logger.debug(f"Draw user profile card for {user_dict}")
    return await template_to_pic(
        template_path=str(Path(__file__).parent / "templates"),
        template_name="player.html",
        templates={"user": user_dict},
    )
