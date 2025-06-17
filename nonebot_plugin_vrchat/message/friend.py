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
) -> bytes:
    """生成用户组卡片概览图。

    参数:
        users (List[LimitedUserModel]): 用户列表，每个用户应为LimitedUserModel实例。
        group (bool, optional): 是否按状态分组。默认为True，将按照STATUS_DESC_MAP的顺序排序和分组。

    返回:
        bytes: 生成的图片二进制数据。

    处理逻辑包括：
    1. 根据用户状态分组。
    2. 如果group为True，则根据STATUS_DESC_MAP定义的顺序对用户进行排序；否则将所有用户归类到'unknown'键下。
    3. 对每组用户按照信任等级进行降序排序。
    4. 使用模板生成最终的图片。
    """
    time_now = datetime.now(timezone.utc)
    user_dict: Dict[str, List[LimitedUserModel]] = {}
    # logger.debug(f"user_dict: {user_dict}")
    for user in users:
        logger.debug(f"user: {user.location}")
        # 标题
        loc = ""
        content = user.status_description or STATUS_DESC_MAP[user.status]
        if user.status in OFFLINE_STATUSES:
            if user.last_login:
                delta = time_now - user.last_login
                content = f"{content}\n{td_format(delta)}"
        elif user.status != "webonline" and user.location:
            loc = await format_location(client, user.location)
            content = f"{content}\n{loc}"

        logger.debug(f"content: {content}")

        # 世界地点
        user.location = content
        user_dict.setdefault(user.status, []).append(user)

    # 按 STATUS_DESC_MAP 顺序排序
    user_dict = (
        {k: user_dict[k] for k in STATUS_DESC_MAP if k in user_dict}
        if group
        else {"unknown": [x for y in user_dict.values() for x in y]}
    )

    # 按信任等级排序
    trust_keys = list(TRUST_COLORS.keys())
    for li in user_dict.values():
        li.sort(key=lambda x: trust_keys.index(x.trust), reverse=True)

    # 传递 user_dict 和状态描述到模板
    logger.debug(f"Draw user card overview for {len(users)} users")
    logger.debug(f"user_dict: {user_dict}")
    logger.debug(f"status_desc_map: {STATUS_DESC_MAP}")
    return await template_to_pic(
        template_path=str(Path(__file__).parent / "templates"),
        template_name="friend_list.html",
        templates={
            "user_dict": user_dict,
            "status_desc_map": STATUS_DESC_MAP,
            "status_colors": STATUS_COLORS,
        },
        wait=1,
    )


async def draw_user_profile_card(user) -> bytes:
    """
    用 HTML 渲染个人信息卡片图片（适配 LimitedUserModel）
    :param user: LimitedUserModel 实例或 dict
    :return: 图片的二进制内容
    """
    # 若为 Pydantic/BaseModel，转为 dict
    if hasattr(user, "dict"):
        user = user.dict()
    elif hasattr(user, "__dict__"):
        user = user.__dict__

    return await template_to_pic(
        template_path=str(Path(__file__).parent / "templates"),
        template_name="player.html",
        templates={"user": user},
    )
