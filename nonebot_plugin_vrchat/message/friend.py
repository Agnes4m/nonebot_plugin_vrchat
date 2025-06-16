from pathlib import Path
from typing import Dict, List, Optional

from nonebot import logger
from nonebot_plugin_htmlrender import template_to_pic

from ..vrchat import ApiClient, LimitedUserModel, NormalizedStatusType, random_client
from .utils import STATUS_DESC_MAP, TRUST_COLORS


async def draw_user_card_overview(
    users: List[LimitedUserModel],
    group: bool = True,
    client: Optional[ApiClient] = None,
) -> bytes:
    """
    用 HTML 渲染好友总览卡片并转为图片，按状态分组
    :param users: 好友信息列表
    :param group: 是否分组显示
    :param client: VRCClient 实例
    :return: 图片的二进制内容
    """
    if not client:
        client = await random_client()

    user_dict: Dict[NormalizedStatusType, List[LimitedUserModel]] = {}
    for user in users:
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
        templates={"user_dict": user_dict, "status_desc_map": STATUS_DESC_MAP},
    )
