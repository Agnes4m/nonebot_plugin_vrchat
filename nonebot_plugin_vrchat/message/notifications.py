from typing import List, Optional

from vrchatapi import Notification

from ..vrchat import ApiClient


async def draw_notification_card(
    ntfs: List[Notification],
    client: Optional[ApiClient] = None,
):
    ...
    # 渲染图片
    # return await t2p(
    #     template_path=str(Path(__file__).parent / "templates"),
    #     template_name="friend_list.html",
    #     templates={
    #         "user_dict": user_dict,
    #         "status_desc_map": S_DESC,
    #         "status_colors": S_COLORS,
    #         "trust_colors": T_COLORS,
    #         "title": title,
    #     },
    #     device_scale_factor=1,
    #     screenshot_timeout=60000,
    # )
