from pathlib import Path
from typing import Dict, Optional, TypeVar
from typing_extensions import ParamSpec

import httpx

from ..vrchat import NormalizedStatusType, TrustType

T = TypeVar("T")
P = ParamSpec("P")


STATUS_COLORS: Dict[NormalizedStatusType, str] = {
    "online": "#51e57e",
    "webonline": "#51e57e",
    "joinme": "#42caff",
    "busy": "#5b0b0b",
    "askme": "#e88134",
    "offline": "gray",
    "unknown": "gray",
}
TRUST_COLORS: Dict[TrustType, str] = {
    "visitor": "#cccccc",
    "new": "#1778ff",
    "user": "#2bcf5c",
    "known": "#ff7b42",
    "trusted": "#8143e6",
    "friend": "#ffff00",
    "developer": "#b52626",
    "moderator": "#b52626",
}
STATUS_DESC_MAP: Dict[NormalizedStatusType, str] = {
    "online": "在线",
    "joinme": "欢迎加入",
    "busy": "请勿打扰",
    "askme": "请先询问",
    "webonline": "网页在线",
    "offline": "离线",
    "unknown": "未知",
}
OFFLINE_STATUSES = ["offline", "unknown"]
UNKNOWN_WORLD_TIP = "未知世界"
LOCATION_TRAVELING_TIP = "加载世界中"
LOCATION_PRIVATE_TIP = "私人世界"
LOCATION_INVITE_PREFIX = "邀"
LOCATION_INVITE_PLUS_PREFIX = "邀+"
LOCATION_FRIENDS_PREFIX = "友"
LOCATION_FRIENDS_PLUS_PREFIX = "友+"
LOCATION_PUB_PREFIX = "公"
LOCATION_GROUP_PREFIX = "群"
LOCATION_GROUP_PLUS_PREFIX = "群+"
LOCATION_GROUP_PUB_PREFIX = "群公"

RES_IMG_PATH = Path(__file__).parent / "img"
DEFAULT_IMG_PATH = RES_IMG_PATH / "default_img.png"
USER_ICON_PATH = RES_IMG_PATH / "fa-users-40px.png"

BG_COLOR = (5, 5, 5)
# endregion


# region user card & overview const
USER_CARD_BG_COLOR = (36, 42, 49)
USER_CARD_TITLE_COLOR = (9, 93, 106)
USER_CARD_FONT_COLOR = "#f8f9fa"
USER_AVATAR_BORDER_COLOR = "gray"
USER_AVATAR_WEB_ONLINE_BORDER_COLOR = "#ebd23b"
USER_AVATAR_ONLINE_BORDER_COLOR = "#67d781"
OVERVIEW_TITLE_COLOR = (248, 249, 250)

USER_CARD_SIZE = (710, 190)
USER_CARD_PADDING = 30
USER_CARD_BORDER_RADIUS = 8
USER_CARD_BORDER_WIDTH = 4
USER_CARD_MARGIN = 16

USER_AVATAR_SIZE = (248, 140)
USER_AVATAR_BORDER_RADIUS = 8
USER_AVATAR_BORDER_WIDTH = 4
USER_AVATAR_BG_BLUR = 20
USER_AVATAR_MARGIN_RIGHT = 20

USER_STATUS_SIZE = 30
USER_STATUS_PADDING = 20

USER_TITLE_FONT_SIZE = 32
USER_TEXT_FONT_SIZE = 30
OVERVIEW_TITLE_FONT_SIZE = 36

OVERVIEW_MAX_CARDS_PER_LINE = 2
# endregion


# region group card const
GROUP_TOP_BG_COLOR = (37, 42, 48)
GROUP_BOTTOM_BG_COLOR = (24, 27, 31)
GROUP_TITLE_COLOR = (255, 255, 255)
GROUP_CONTENT_COLOR = (115, 115, 114)
GROUP_ICON_BORDER_COLOR = (24, 27, 31)

GROUP_CARD_SIZE = (640, 485)
GROUP_CARD_PADDING = 10
GROUP_BANNER_SIZE = (620, 205)
GROUP_CARD_BORDER_RADIUS = 16
GROUP_BANNER_BORDER_RADIUS = 16
GROUP_CARD_TOP_HEIGHT = 290
GROUP_CARD_TOP_PADDING_BOTTOM = 20
GROUP_TITLE_MARGIN_LEFT = 200
GROUP_TITLE_MARGIN_BOTTOM = 20
GROUP_ICON_SIZE = 138
GROUP_ICON_BORDER_WIDTH = 6
GROUP_ICON_MARGIN_LEFT = 26
GROUP_ICON_BOTTOM_PLUS = 64
GROUP_FOOTER_HEIGHT = 40
GROUP_FOOTER_PADDING_LEFT = 40

GROUP_TITLE_TEXT_SIZE = 38
GROUP_CONTENT_TEXT_SIZE = 26
# endregion


async def fetch_image_bytes(url: str, timeout: float = 3.0) -> Optional[bytes]:
    """
    异步检测图片URL是否可访问（状态码200且Content-Type为图片）
    :param url: 图片URL
    :param timeout: 超时时间（秒）
    :return: 可访问返回True，否则False
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.head(url)
            if resp.status_code == 200 and resp.headers.get(
                "content-type",
                "",
            ).startswith("image"):
                return resp.content

            resp = await client.get(url)
            if resp.status_code == 200 and resp.headers.get(
                "content-type",
                "",
            ).startswith("image"):
                return resp.content
    except Exception:
        return None
