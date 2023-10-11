import asyncio
from asyncio import Semaphore
from dataclasses import dataclass
from io import BytesIO
from math import ceil
from typing import (
    Awaitable,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
)

import vrchatapi
from async_lru import alru_cache
from httpx import AsyncClient
from nonebot import logger
from PIL.ImageFilter import GaussianBlur
from pil_utils import BuildImage, Text2Image

T = TypeVar("T")

StatusType = Literal[
    "online",
    "webonline",
    "joinme",
    "busy",
    "askme",
    "offline",
    "unknown",
]
TrustType = Literal[
    "visitor",
    "new",
    "user",
    "known",
    "trusted",
    "friend",
    "developer",
    "moderator",
]

BG_COLOR = (5, 5, 5)
CARD_BG_COLOR = (36, 42, 49)
CARD_TITLE_COLOR = (9, 93, 106)
CARD_FONT_COLOR = "#f8f9fa"
AVATAR_BORDER_COLOR = "gray"
AVATAR_ONLINE_BORDER_COLOR = "#ebd23b"
OVERVIEW_TITLE_COLOR = (248, 249, 250)
STATUS_COLORS: Dict[StatusType, str] = {
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

CARD_SIZE = (710, 190)
CARD_PADDING = 30
CARD_BORDER_RADIUS = 8
CARD_BORDER_WIDTH = 4
CARD_MARGIN = 16

AVATAR_SIZE = (248, 140)
AVATAR_BORDER_RADIUS = 8
AVATAR_BORDER_WIDTH = 4
AVATAR_BG_BLUR = 20
AVATAR_MARGIN_RIGHT = 20

STATUS_SIZE = 30
STATUS_PADDING = 20

TITLE_FONT_SIZE = 32
TEXT_FONT_SIZE = 30
OVERVIEW_TITLE_FONT_SIZE = 36

MAX_CARDS_PER_LINE = 2

NORMALIZE_STATUS_MAP: Dict[str, StatusType] = {
    "active": "online",
    "join me": "joinme",
    "do not disturb": "busy",
    "ask me": "askme",
}
STATUS_DESC_MAP: Dict[StatusType, str] = {
    "online": "在线",
    "webonline": "网页在线",
    "joinme": "欢迎加入",
    "busy": "请勿打扰",
    "askme": "请先询问",
    "offline": "离线",
    "unknown": "未知",
}
NORMALIZE_TRUST_MAP: Dict[str, TrustType] = {
    "veteran": "trusted",
    "trusted": "known",
    "known": "user",
}
DEVELOPER_TYPE_MAP: Dict[str, TrustType] = {
    "internal": "developer",
    "moderator": "moderator",
}
OFFLINE_STATUSES = ["offline", "unknown"]
TRUST_TAG_PREFIX = "system_trust_"


def normalize_status(status: str, location: str) -> StatusType:
    if location == "offline":
        if status == "active":
            return "webonline"
        return "offline"
    return NORMALIZE_STATUS_MAP.get(status, "unknown")


def extract_trust_level(tags: List[str], developer_type: str) -> TrustType:
    if developer_type in DEVELOPER_TYPE_MAP:
        return DEVELOPER_TYPE_MAP[developer_type]

    for suffix in NORMALIZE_TRUST_MAP:
        if f"{TRUST_TAG_PREFIX}{suffix}" in tags:
            return NORMALIZE_TRUST_MAP[suffix]

    return "visitor"


def chunks(lst: Sequence[T], n: int) -> Iterator[Sequence[T]]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def with_semaphore(semaphore: Semaphore):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            async with semaphore:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def get_fittable_text(text: str, size: int, max_width: int, **kwargs) -> Text2Image:
    text_obj = Text2Image.from_text(text, size, **kwargs)
    if text_obj.width <= max_width:
        return text_obj

    while True:
        if not text:
            raise ValueError("max_width too small")
        text = text[:-1]
        text_obj = Text2Image.from_text(text + "...", size, **kwargs)
        if text_obj.width <= max_width:
            return text_obj


@dataclass
class UserInfo:
    name: str
    avatar_url: str
    status: StatusType
    status_desc: str
    trust: TrustType

    @classmethod
    def from_limited_user(cls, user: vrchatapi.LimitedUser) -> "UserInfo":
        logger.debug(f"User: {user.to_dict()}")
        if not (
            user.current_avatar_thumbnail_image_url
            and user.display_name
            and user.status
            and user.location
            and user.tags
            and user.developer_type
        ):
            raise ValueError("Invalid user")

        status = normalize_status(user.status, user.location)
        trust = extract_trust_level(user.tags, user.developer_type)
        return cls(
            avatar_url=user.current_avatar_thumbnail_image_url,
            name=user.display_name,
            status=status,
            status_desc=user.status_description or STATUS_DESC_MAP[status],
            trust=trust,
        )


@alru_cache()
async def get_url_bytes(url: str) -> bytes:
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
        return resp.content


async def draw_user_card_on_image(
    user: UserInfo,
    image: BuildImage,
    pos: Tuple[int, int],
) -> BuildImage:
    avatar_img = BuildImage.open(BytesIO(await get_url_bytes(user.avatar_url)))

    offset_x, offset_y = pos
    card_w, card_h = CARD_SIZE

    # card border and bg
    image.draw_rounded_rectangle(
        (offset_x, offset_y, offset_x + card_w, offset_y + card_h),
        CARD_BORDER_RADIUS,
        fill=CARD_BG_COLOR,
        outline=TRUST_COLORS[user.trust],
        width=CARD_BORDER_WIDTH,
    )

    # avatar
    avatar_w, avatar_h = AVATAR_SIZE
    avatar_y = card_h // 2 - avatar_h // 2
    if not abs((avatar_w / avatar_h) - (avatar_img.width / avatar_img.height)) < 0.1:
        # print(f"draw bg blur for user {user.name}")
        image.paste(
            avatar_img.copy()
            .resize(AVATAR_SIZE, keep_ratio=True)
            .filter(GaussianBlur(AVATAR_BG_BLUR)),
            (offset_x + CARD_PADDING, offset_y + avatar_y),
        )
    image.paste(
        avatar_img.copy().resize(AVATAR_SIZE, keep_ratio=True, inside=True),
        (offset_x + CARD_PADDING, offset_y + avatar_y),
        alpha=True,
    )
    image.draw_rounded_rectangle(
        (
            offset_x - CARD_BORDER_WIDTH + CARD_PADDING,
            offset_y - CARD_BORDER_WIDTH + avatar_y,
            offset_x + CARD_BORDER_WIDTH - 1 + CARD_PADDING + avatar_w,
            offset_y + CARD_BORDER_WIDTH - 1 + avatar_y + avatar_h,
        ),
        AVATAR_BORDER_RADIUS,
        outline=(
            AVATAR_BORDER_COLOR
            if user.status in OFFLINE_STATUSES
            else AVATAR_ONLINE_BORDER_COLOR
        ),
        width=4,
    )

    # title & content
    content_x = CARD_PADDING + CARD_BORDER_WIDTH * 2 + avatar_w + AVATAR_MARGIN_RIGHT
    title_x = content_x + STATUS_SIZE + STATUS_PADDING
    title_width = card_w - title_x - CARD_PADDING
    content_width = card_w - content_x - CARD_PADDING
    title_text = get_fittable_text(
        user.name,
        TITLE_FONT_SIZE,
        title_width,
        fill=CARD_TITLE_COLOR,
        weight="bold",
    )
    content_text = get_fittable_text(
        user.status_desc,
        TEXT_FONT_SIZE,
        content_width,
        fill=CARD_FONT_COLOR,
    )
    line_space = (
        card_h - CARD_PADDING * 2 - title_text.height - content_text.height
    ) // 3
    title_y = CARD_PADDING + line_space
    content_y = title_y + title_text.height + line_space
    title_text.draw_on_image(image.image, (offset_x + title_x, offset_y + title_y))
    content_text.draw_on_image(
        image.image,
        (offset_x + content_x, offset_y + content_y),
    )

    # status
    status_color = STATUS_COLORS[user.status]
    status_y_offset = title_y - (STATUS_SIZE - title_text.height) // 2
    status_x = content_x
    image.draw_ellipse(
        (
            offset_x + status_x,
            offset_y + status_y_offset,
            offset_x + status_x + STATUS_SIZE,
            offset_y + status_y_offset + STATUS_SIZE,
        ),
        fill=status_color,
    )

    return image


def transform_limited_users(users: List[vrchatapi.LimitedUser]) -> List[UserInfo]:
    def trans(it: vrchatapi.LimitedUser) -> Optional[UserInfo]:
        try:
            return UserInfo.from_limited_user(it)
        except ValueError:
            logger.warning(f"Invalid user: {it.to_dict()}")
            return None

    return [x for x in (trans(user) for user in users) if x]


async def draw_user_card_overview(
    users: List[UserInfo],
    group: bool = True,
) -> BuildImage:
    user_dict: Dict[StatusType, List[UserInfo]] = {}
    for user in users:
        user_dict.setdefault(user.status, []).append(user)

    # sort online status
    user_dict = dict(
        ((k, user_dict[k]) for k in STATUS_DESC_MAP if k in user_dict)
        if group
        else (("unknown", [x for y in user_dict.values() for x in y]),),
    )

    # sort trust level
    trust_keys = list(TRUST_COLORS.keys())
    for li in user_dict.values():
        li.sort(key=lambda x: trust_keys.index(x.trust), reverse=True)

    card_w, card_h = CARD_SIZE
    width_multiplier = max((len(x) for x in user_dict.values()), default=0)
    if width_multiplier > MAX_CARDS_PER_LINE:
        width_multiplier = MAX_CARDS_PER_LINE

    title_h = 49
    width = width_multiplier * card_w + (width_multiplier + 1) * CARD_MARGIN
    height = CARD_MARGIN
    for users in user_dict.values():
        height_multiplier = ceil(len(users) / width_multiplier)
        height += (
            (
                title_h
                + height_multiplier * card_h
                + (height_multiplier + 1) * CARD_MARGIN
            )
            if group
            else (height_multiplier * card_h + height_multiplier * CARD_MARGIN)
        )

    image = BuildImage.new("RGBA", (width, height), BG_COLOR)
    tasks: List[Awaitable] = []
    semaphore = Semaphore(8)

    y_offset = CARD_MARGIN
    for status, users in user_dict.items():
        if group:
            title_text = Text2Image.from_text(
                f"{STATUS_DESC_MAP[status]} ({len(users)})",
                OVERVIEW_TITLE_FONT_SIZE,
                fill=OVERVIEW_TITLE_COLOR,
                weight="bold",
            )
            title_text.draw_on_image(image.image, (CARD_MARGIN, y_offset))
            y_offset += title_h + CARD_MARGIN

        for line in chunks(users, width_multiplier):
            x_offset = CARD_MARGIN
            for user in line:
                tasks.append(
                    with_semaphore(semaphore)(draw_user_card_on_image)(
                        user,
                        image,
                        (x_offset, y_offset),
                    ),
                )
                x_offset += card_w + CARD_MARGIN
            y_offset += card_h + CARD_MARGIN

    await asyncio.gather(*tasks)

    return image


def i2b(img: BuildImage, img_format: str = "JPEG") -> BytesIO:
    if img_format.lower() == "jpeg":
        img = img.convert("RGB")
    return img.save(img_format)


async def draw_user_profile(user: vrchatapi.User) -> BuildImage:
    bg = BuildImage.new("RGBA", (500, 500), BG_COLOR)
    bg.draw_text((5, 5), f"User: {user.display_name}\nWorking in progress")
    return bg
