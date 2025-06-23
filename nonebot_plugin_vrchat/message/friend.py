from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from nonebot import logger
from nonebot_plugin_htmlrender import template_to_pic as t2p

from ..config import env_config
from ..vrchat import ApiClient, LimitedUserModel, UserModel
from .utils import OFFLINE_STATUSES as OFFLINE
from .utils import PLATFORM_DESC as P_DESC
from .utils import STATUS_COLORS as S_COLORS
from .utils import STATUS_DESC_MAP as S_DESC
from .utils import TRUST_COLORS as T_COLORS
from .utils import (
    FriendListTemplateContext,
    convert_urls_to_base64,
    get_avatar_url,
    select_friend_html,
)
from .utils import format_location as fmt_loc
from .utils import td_format as td_fmt

template_path = str(Path(__file__).parent / "templates")


async def draw_user_card_overview(
    users: List[LimitedUserModel],
    group: bool = True,
    client: Optional[ApiClient] = None,
    title: str = "好友列表",
):
    time_now = datetime.now(timezone.utc)
    raw_user_dict: Dict[str, List[dict]] = {}
    logger.debug(f"用户数量: {len(users)}")
    for idx, user in enumerate(users):
        # 计算location_content
        if user.status in OFFLINE:
            if user.last_login:
                delta = time_now - user.last_login
                location_content = td_fmt(delta)
            else:
                location_content = "离线"
        elif user.status != "webonline" and user.location:
            location_content = await fmt_loc(client, user.location)
        else:
            location_content = "离线"

        effective_status = (
            "offline"
            if user.status == "unknown" and user.original_status == "offline"
            else user.status
        )
        raw_user_dict.setdefault(effective_status, []).append(
            {
                "index": idx + 1,
                "location": location_content,
                "original_status": user.original_status,
                "status_description": user.status_description,
                "display_name": user.display_name,
                "current_avatar_thumbnail_image_url": user.current_avatar_thumbnail_image_url,
                "trust": user.trust,
            },
        )

    # 排序
    if group:
        user_dict = {k: raw_user_dict[k] for k in S_DESC if k in raw_user_dict}
        trust_keys = list(T_COLORS.keys())
        for li in user_dict.values():
            li.sort(key=lambda x: trust_keys.index(x["trust"]), reverse=True)
    else:
        user_dict = {"unknown": [x for y in raw_user_dict.values() for x in y]}

    user_dict = await convert_urls_to_base64(user_dict)
    # 渲染图片
    templates: FriendListTemplateContext = {
        "user_dict": user_dict,
        "status_desc_map": S_DESC,
        "status_colors": S_COLORS,
        "trust_colors": T_COLORS,
        "title": title,
    }
    # logger.debug(f"Draw user list card for {templates}")
    return await t2p(
        template_path=str(Path(__file__).parent / "templates"),
        template_name=await select_friend_html(env_config.vrchat_img),
        templates=templates,
        device_scale_factor=1,
        screenshot_timeout=60_000,
    )


async def draw_user_profile_card(user: UserModel) -> bytes:
    """单人信息卡片渲染"""
    time_now = datetime.now(timezone.utc)
    logger.debug(f"UserModel: {dict(user)}")
    content = user.status_description or ""
    # 计算location内容
    if user.status in OFFLINE:
        if user.last_login:
            last_login_dt = user.last_login
            if isinstance(last_login_dt, str):
                last_login_dt = datetime.fromisoformat(last_login_dt)
            delta = time_now - last_login_dt
            content = f"{content}\n{td_fmt(delta)}"
    elif user.status != "webonline" and user.location:
        loc = await fmt_loc(None, user.location)
        content = f"{content}\n{loc}"

    user_dict = {
        "location": content,
        "original_status": user.status,
        "status_description": user.status_description,
        "display_name": user.display_name,
        "current_avatar_thumbnail_image_url": await get_avatar_url(
            user.current_avatar_thumbnail_image_url,
        ),
        "trust": user.trust,
        "last_platform": user.last_platform,
        "bio": user.bio or "",
        "age_verified": user.age_verified,
        "date_joined": user.date_joined.isoformat() if user.date_joined else "",
        "is_friend": user.is_friend,
    }
    logger.debug(f"Draw user profile card for {user_dict}")
    return await t2p(
        template_path=str(Path(__file__).parent / "templates"),
        template_name="player.html",
        templates={
            "user": user_dict,
            "status_colors": S_COLORS,
            "trust_colors": T_COLORS,
            "last_platform": P_DESC,
            "status_desc_map": S_DESC,
        },
        screenshot_timeout=60_000,
    )
