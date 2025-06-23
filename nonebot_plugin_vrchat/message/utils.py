import asyncio
import base64
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple, TypedDict, TypeVar
from typing_extensions import ParamSpec

import aiohttp
import httpx
from async_lru import alru_cache
from httpx import AsyncClient
from nonebot.log import logger
from PIL import Image

from nonebot_plugin_vrchat.config import env_config

from ..i18n.model import Lang
from ..vrchat import (
    ApiClient,
    LimitedUserModel,
    NormalizedStatusType,
    TrustType,
    get_world,
)

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
    "online": Lang.nbp_vrc.words.online(),
    "joinme": Lang.nbp_vrc.words.joinme(),
    "busy": Lang.nbp_vrc.words.busy(),
    "askme": Lang.nbp_vrc.words.askme(),
    "webonline": Lang.nbp_vrc.words.webonline(),
    "offline": Lang.nbp_vrc.words.offline(),
    "unknown": Lang.nbp_vrc.words.unknown(),
}

PLATFORM_DESC = {
    "standalonewindows": Lang.nbp_vrc.words.standalonewindows(),
    "android": Lang.nbp_vrc.words.android(),
    "oculus": Lang.nbp_vrc.words.oculus(),
    "unknownplatform": Lang.nbp_vrc.words.unknown(),
}
OFFLINE_STATUSES = ["offline", "unknown"]
UNKNOWN_WORLD_TIP = Lang.nbp_vrc.words.unkown_world()
LOCATION_TRAVELING_TIP = Lang.nbp_vrc.words.travel_world()
LOCATION_PRIVATE_TIP = Lang.nbp_vrc.words.private_world()
LOCATION_INVITE_PREFIX = Lang.nbp_vrc.words.invite()
LOCATION_INVITE_PLUS_PREFIX = f"{LOCATION_INVITE_PREFIX}+"
LOCATION_FRIENDS_PREFIX = Lang.nbp_vrc.words.friends()
LOCATION_FRIENDS_PLUS_PREFIX = f"{LOCATION_FRIENDS_PREFIX}+"
LOCATION_PUB_PREFIX = Lang.nbp_vrc.words.pub()
LOCATION_GROUP_PREFIX = Lang.nbp_vrc.words.group()
LOCATION_GROUP_PLUS_PREFIX = f"{LOCATION_GROUP_PREFIX}+"
LOCATION_GROUP_PUB_PREFIX = Lang.nbp_vrc.words.group_pub()

RES_IMG_PATH = Path(__file__).parent.parent / "img"
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


async def format_location(client: Optional[ApiClient], location: Optional[str]):
    if not location:
        return ""
    if location == "traveling":
        return LOCATION_TRAVELING_TIP
    if location == "private":
        return LOCATION_PRIVATE_TIP

    world_id = location.split(":")[0]
    # logger.debug(f"location: {location}, world_id: {world_id}")
    region = (
        location[location.find("region(") + 7 : location.find(")")].upper()
        if "region(" in location
        else None
    )

    if "group" in location:
        if "groupAccessType(members)" in location:
            prefix = LOCATION_GROUP_PREFIX
        elif "groupAccessType(plus)" in location:
            prefix = LOCATION_GROUP_PLUS_PREFIX
        else:  # elif "groupAccessType(public)" in location:
            prefix = LOCATION_GROUP_PUB_PREFIX

    elif "private" in location:
        if "canRequestInvite" in location:
            prefix = LOCATION_INVITE_PLUS_PREFIX
        else:
            prefix = LOCATION_INVITE_PREFIX

    elif "friends" in location:
        prefix = LOCATION_FRIENDS_PREFIX

    elif "hidden" in location:
        prefix = LOCATION_FRIENDS_PLUS_PREFIX

    else:
        prefix = LOCATION_PUB_PREFIX
    try:
        if client is not None:
            world = await get_world(client, world_id)
            world_name = world.name
        else:
            world_name = UNKNOWN_WORLD_TIP
    except Exception as e:
        world_name = UNKNOWN_WORLD_TIP
        logger.exception(
            f"Failed to get info of world `{world_id}`: {type(e).__name__}: {e}",
        )

    ret = f"{prefix} |"
    if region:
        ret = f"{ret} {region} |"
    return f"{ret}\n{world_name}"


def td_format(td_object: timedelta):
    seconds = int(td_object.total_seconds())
    periods = [
        (Lang.nbp_vrc.time.year(), 60 * 60 * 24 * 365),
        (Lang.nbp_vrc.time.month(), 60 * 60 * 24 * 30),
        (Lang.nbp_vrc.time.day(), 60 * 60 * 24),
        (Lang.nbp_vrc.time.hour(), 60 * 60),
        (Lang.nbp_vrc.time.minute(), 60),
        (Lang.nbp_vrc.time.second(), 1),
    ]

    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            return f"{period_value}{period_name}前上线"

    return "很久没上线"


async def get_image_or_default(
    url: Optional[str],
    default_size: Optional[Tuple[int, int]] = None,
    # default_img_path: Optional[Path] = None,
):
    img = None

    if url:
        try:
            img = await get_url_bytes(url, default_size=default_size)
        except Exception as e:
            logger.warning(
                f"Failed to get image, url `{url}`: {type(e).__name__}: {e}",
            )

    if not img:
        return None
        # img_path = default_img_path or DEFAULT_IMG_PATH
        # async with aiofiles.open(img_path, "rb") as f:
        #     img = await f.read()
        # if default_size:

        #     with Image.open(BytesIO(img)) as im:
        #         im = im.convert("RGBA")
        #         im.thumbnail(default_size, Image.Resampling.LANCZOS)
        #         buf = BytesIO()
        #         im.save(buf, format="PNG")
        #         img = buf.getvalue()

    return f"{base64.b64encode(img).decode('utf-8')}"


@alru_cache()
async def get_url_bytes(
    url: str,
    default_size: Optional[Tuple[int, int]] = None,
) -> bytes:
    async with AsyncClient(
        follow_redirects=True,
        headers={
            "Referer": "https://vrchat.com/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/117.0.0.0 "
                "Safari/537.36"
            ),
        },
    ) as cli:
        resp = await cli.get(url)
        resp.raise_for_status()
        img_bytes = resp.content
        if default_size:
            with Image.open(BytesIO(img_bytes)) as img:
                img = img.convert("RGBA")
                img.thumbnail(default_size, Image.Resampling.LANCZOS)
                buf = BytesIO()
                img.save(buf, format="PNG")
                return buf.getvalue()
        return img_bytes


def cols_get(cols: int):
    if cols <= 6:
        return 1
    if cols <= 26:
        return 2
    if cols <= 125:
        return 3
    return 4


class FriendListTemplateContext(TypedDict):
    user_dict: Dict[str, List[LimitedUserModel]]
    status_desc_map: NormalizedStatusType
    status_colors: NormalizedStatusType
    trust_colors: TrustType
    title: str


async def get_avatar_url(url: str) -> str:
    if env_config.vrchat_avatar is False:
        return "default.png"
    vrchat_prefix = "https://api.vrchat.cloud/api/1/image/"
    if url and url.startswith(vrchat_prefix):
        try:
            return await url_to_base64(url)
        except Exception:
            return "default.png"
    return "default.png"


async def url_to_base64(url: str) -> Optional[str]:
    """将图片URL转换为Base64编码，添加请求头防止403错误"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://vrchat.com/",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with (
            aiohttp.ClientSession(headers=headers) as session,
            session.get(url, timeout=timeout) as response,
        ):
            if response.status == 403:
                logger.warning(f"403 Forbidden: {url}")
                return None

            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                logger.info(f"Invalid content type: {content_type}")
                return None

            image_data = await response.read()
            return base64.b64encode(image_data).decode("utf-8")

    except Exception as e:
        print(f"Error converting URL to Base64: {url} - {e!s}")
        return None


async def convert_urls_to_base64(data: Dict) -> Dict:
    """转换所有图片URL为Base64格式"""
    result = {
        status: [dict(entry) for entry in entries] for status, entries in data.items()
    }

    tasks = []
    url_mapping = []

    for status, entries in result.items():
        for idx, entry in enumerate(entries):
            url = entry.get("current_avatar_thumbnail_image_url")
            if url and url != "default.png":
                # tasks.append(url_to_base64(url))
                tasks.append(get_image_or_default(url))
                url_mapping.append((status, idx))

    base64_results = await asyncio.gather(*tasks)

    # 更新结果数据
    for (status, idx), base64_data in zip(url_mapping, base64_results):
        if base64_data:
            result[status][idx][
                "current_avatar_thumbnail_image_url_base64"
            ] = f"data:image/png;base64,{base64_data}"
        else:
            result[status][idx]["current_avatar_thumbnail_image_url"] = "default.png"
            result[status][idx].pop("current_avatar_thumbnail_image_url_base64", None)

    return result


async def select_friend_html(tag: str):
    if tag == "default":
        return "friend_list_default.html"
    return "friend_list.html"
