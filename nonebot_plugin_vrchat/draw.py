import asyncio
from asyncio import Semaphore
from datetime import datetime, timedelta, timezone
from io import BytesIO
from math import ceil, isclose
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
)

from async_lru import alru_cache
from httpx import AsyncClient
from nonebot import logger
from PIL.ImageFilter import GaussianBlur
from pil_utils import BuildImage, Text2Image

from .vrchat import get_world, random_client

if TYPE_CHECKING:
    from .vrchat.types import (
        GroupModel,
        LimitedUserModel,
        NormalizedStatusType,
        TrustType,
        UserModel,
    )

# region common const & type
T = TypeVar("T")


STATUS_COLORS: Dict["NormalizedStatusType", str] = {
    "online": "#51e57e",
    "webonline": "#51e57e",
    "joinme": "#42caff",
    "busy": "#5b0b0b",
    "askme": "#e88134",
    "offline": "gray",
    "unknown": "gray",
}
TRUST_COLORS: Dict["TrustType", str] = {
    "visitor": "#cccccc",
    "new": "#1778ff",
    "user": "#2bcf5c",
    "known": "#ff7b42",
    "trusted": "#8143e6",
    "friend": "#ffff00",
    "developer": "#b52626",
    "moderator": "#b52626",
}
STATUS_DESC_MAP: Dict["NormalizedStatusType", str] = {
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


# region user detail const
# endregion


# region util funcs & classes


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


def i2b(img: BuildImage, img_format: str = "JPEG") -> BytesIO:
    if img_format.lower() == "jpeg":
        img = img.convert("RGB")
    return img.save(img_format)


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


async def get_image_or_default(
    url: Optional[str],
    default_size: Optional[Tuple[int, int]] = None,
    default_img_path: Optional[Path] = None,
) -> BuildImage:
    img = None

    if url:
        try:
            img = BuildImage.open(BytesIO(await get_url_bytes(url)))
        except Exception as e:
            logger.warning(
                f"Failed to get image, url `{url}`: {type(e).__name__}: {e}",
            )

    if not img:
        img_path = default_img_path or DEFAULT_IMG_PATH
        img = BuildImage.open(BytesIO(img_path.read_bytes()))
        if default_size:
            img = img.resize(default_size, keep_ratio=True, inside=True)

    return img


async def format_location(location: str) -> str:
    if location == "traveling":
        return LOCATION_TRAVELING_TIP
    if location == "private":
        return LOCATION_PRIVATE_TIP

    world_id = location[: location.find(":")]
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
        world = await get_world(random_client(), world_id)
        world_name = world.name
    except Exception as e:
        world_name = UNKNOWN_WORLD_TIP
        logger.exception(
            f"Failed to get info of world `{world_id}`: {type(e).__name__}: {e}",
        )

    ret = f"{prefix}|"
    if region:
        ret = f"{ret}{region}|"
    return f"{ret}{world_name}"


def td_format(td_object: timedelta):
    seconds = int(td_object.total_seconds())
    periods = [
        ("年", 60 * 60 * 24 * 365),
        ("月", 60 * 60 * 24 * 30),
        ("日", 60 * 60 * 24),
        ("小时", 60 * 60),
        ("分钟", 60),
        ("秒", 1),
    ]

    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            return f"{period_value}{period_name}前上线"

    return "很久没上线"


# endregion


# region draw funcs


async def draw_user_card_on_image(
    user: "LimitedUserModel",
    image: BuildImage,
    pos: Tuple[int, int],
) -> BuildImage:
    time_now = datetime.now(timezone.utc)

    offset_x, offset_y = pos
    card_w, card_h = USER_CARD_SIZE

    # card border and bg
    image.draw_rounded_rectangle(
        (offset_x, offset_y, offset_x + card_w, offset_y + card_h),
        USER_CARD_BORDER_RADIUS,
        fill=USER_CARD_BG_COLOR,
        outline=TRUST_COLORS[user.trust],
        width=USER_CARD_BORDER_WIDTH,
    )

    # avatar
    avatar_img = (
        await get_image_or_default(
            user.current_avatar_thumbnail_image_url,
            USER_AVATAR_SIZE,
        )
    ).convert("RGBA")
    avatar_w, avatar_h = USER_AVATAR_SIZE
    avatar_y = card_h // 2 - avatar_h // 2
    ratio_resized = avatar_w / avatar_h
    ratio_original = avatar_img.width / avatar_img.height
    # logger.debug(f"Ratio resized: {ratio_resized}, Ratio original: {ratio_original}")
    if not isclose(ratio_resized, ratio_original):
        # logger.debug(f"Draw blur background for user {user.display_name}")
        image.paste(
            (
                avatar_img.copy()
                .resize(USER_AVATAR_SIZE, keep_ratio=True)
                .filter(GaussianBlur(USER_AVATAR_BG_BLUR))
            ),
            (offset_x + USER_CARD_PADDING, offset_y + avatar_y),
        )
    image.paste(
        avatar_img.copy().resize(USER_AVATAR_SIZE, keep_ratio=True, inside=True),
        (offset_x + USER_CARD_PADDING, offset_y + avatar_y),
        alpha=True,
    )
    image.draw_rounded_rectangle(
        (
            offset_x - USER_CARD_BORDER_WIDTH + USER_CARD_PADDING,
            offset_y - USER_CARD_BORDER_WIDTH + avatar_y,
            offset_x + USER_CARD_BORDER_WIDTH - 1 + USER_CARD_PADDING + avatar_w,
            offset_y + USER_CARD_BORDER_WIDTH - 1 + avatar_y + avatar_h,
        ),
        USER_AVATAR_BORDER_RADIUS,
        outline=(
            USER_AVATAR_BORDER_COLOR
            if user.status in OFFLINE_STATUSES
            else (
                USER_AVATAR_WEB_ONLINE_BORDER_COLOR
                if user.status == "webonline"
                else USER_AVATAR_ONLINE_BORDER_COLOR
            )
        ),
        width=4,
    )

    # title & content
    content_x = (
        USER_CARD_PADDING
        + USER_CARD_BORDER_WIDTH * 2
        + avatar_w
        + USER_AVATAR_MARGIN_RIGHT
    )
    content_width = card_w - content_x - USER_CARD_PADDING
    title_x = content_x + USER_STATUS_SIZE + USER_STATUS_PADDING
    title_width = card_w - title_x - USER_CARD_PADDING
    title_text = get_fittable_text(
        user.display_name,
        USER_TITLE_FONT_SIZE,
        title_width,
        fill=USER_CARD_TITLE_COLOR,
        weight="bold",
    )

    content = user.status_description or STATUS_DESC_MAP[user.status]
    if user.status in OFFLINE_STATUSES:
        if user.last_login:
            delta = time_now - user.last_login
            content = f"{content}\n{td_format(delta)}"
    elif user.status != "webonline" and user.location:
        content = f"{content}\n{await format_location(user.location)}"
    content_text = get_fittable_text(
        content,
        USER_TEXT_FONT_SIZE,
        content_width,
        fill=USER_CARD_FONT_COLOR,
    )
    line_space = (
        card_h - USER_CARD_PADDING * 2 - title_text.height - content_text.height
    ) // 3
    title_y = USER_CARD_PADDING + line_space
    content_y = title_y + title_text.height + line_space
    title_text.draw_on_image(image.image, (offset_x + title_x, offset_y + title_y))
    content_text.draw_on_image(
        image.image,
        (offset_x + content_x, offset_y + content_y),
    )

    # status
    status_color = STATUS_COLORS[user.status]
    status_y_offset = title_y - (USER_STATUS_SIZE - title_text.height) // 2
    status_x = content_x
    image.draw_ellipse(
        (
            offset_x + status_x,
            offset_y + status_y_offset,
            offset_x + status_x + USER_STATUS_SIZE,
            offset_y + status_y_offset + USER_STATUS_SIZE,
        ),
        fill=status_color,
    )

    return image


async def draw_user_card_overview(
    users: List["LimitedUserModel"],
    group: bool = True,
) -> BuildImage:
    user_dict: Dict["NormalizedStatusType", List["LimitedUserModel"]] = {}
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

    card_w, card_h = USER_CARD_SIZE
    width_multiplier = max((len(x) for x in user_dict.values()), default=0)
    if width_multiplier > OVERVIEW_MAX_CARDS_PER_LINE:
        width_multiplier = OVERVIEW_MAX_CARDS_PER_LINE

    title_h = 49
    width = width_multiplier * card_w + (width_multiplier + 1) * USER_CARD_MARGIN
    height = USER_CARD_MARGIN
    for users in user_dict.values():
        height_multiplier = ceil(len(users) / width_multiplier)
        height += (
            (
                title_h
                + height_multiplier * card_h
                + (height_multiplier + 1) * USER_CARD_MARGIN
            )
            if group
            else (height_multiplier * card_h + height_multiplier * USER_CARD_MARGIN)
        )

    image = BuildImage.new("RGBA", (width, height), BG_COLOR)
    tasks: List[Awaitable] = []
    semaphore = Semaphore(8)

    y_offset = USER_CARD_MARGIN
    for status, users in user_dict.items():
        if group:
            title_text = Text2Image.from_text(
                f"{STATUS_DESC_MAP[status]} ({len(users)})",
                OVERVIEW_TITLE_FONT_SIZE,
                fill=OVERVIEW_TITLE_COLOR,
                weight="bold",
            )
            title_text.draw_on_image(image.image, (USER_CARD_MARGIN, y_offset))
            y_offset += title_h + USER_CARD_MARGIN

        for line in chunks(users, width_multiplier):
            x_offset = USER_CARD_MARGIN
            for user in line:
                tasks.append(
                    with_semaphore(semaphore)(draw_user_card_on_image)(
                        user,
                        image,
                        (x_offset, y_offset),
                    ),
                )
                x_offset += card_w + USER_CARD_MARGIN
            y_offset += card_h + USER_CARD_MARGIN

    await asyncio.gather(*tasks)

    return image


async def draw_group_on_image(
    group: "GroupModel",
    image: BuildImage,
    pos: Tuple[int, int],
) -> BuildImage:
    offset_x, offset_y = pos
    card_w, card_h = GROUP_CARD_SIZE

    # bg
    image.draw_rounded_rectangle(
        (
            offset_x,
            offset_y,
            offset_x + card_w - 1,
            offset_y + GROUP_CARD_TOP_HEIGHT + GROUP_CARD_BORDER_RADIUS - 1,
        ),
        GROUP_CARD_BORDER_RADIUS,
        fill=GROUP_TOP_BG_COLOR,
    )
    image.draw_rounded_rectangle(
        (
            offset_x,
            offset_y + GROUP_CARD_TOP_HEIGHT,
            offset_x + card_w - 1,
            offset_y + card_h - 1,
        ),
        GROUP_CARD_BORDER_RADIUS,
        fill=GROUP_BOTTOM_BG_COLOR,
    )
    image.draw_rectangle(
        (
            offset_x,
            offset_y + GROUP_CARD_TOP_HEIGHT,
            offset_x + card_w - 1,
            offset_y + GROUP_CARD_TOP_HEIGHT + GROUP_CARD_BORDER_RADIUS - 1,
        ),
        fill=GROUP_BOTTOM_BG_COLOR,
    )

    # banner & icon
    icon_img, banner_img = await asyncio.gather(
        get_image_or_default(group.icon_url, (GROUP_ICON_SIZE, GROUP_ICON_SIZE)),
        get_image_or_default(group.banner_url, GROUP_BANNER_SIZE),
    )
    banner_img = banner_img.resize(
        GROUP_BANNER_SIZE,
        keep_ratio=True,
    ).circle_corner(GROUP_BANNER_BORDER_RADIUS)
    icon_img = icon_img.resize(
        (GROUP_ICON_SIZE, GROUP_ICON_SIZE),
        keep_ratio=True,
    ).circle()

    image.paste(
        banner_img,
        (
            offset_x + GROUP_CARD_PADDING,
            offset_y + GROUP_CARD_PADDING,
        ),
        alpha=True,
    )

    banner_h = GROUP_BANNER_SIZE[1]
    icon_x, icon_y = (
        offset_x + GROUP_CARD_PADDING + GROUP_ICON_MARGIN_LEFT,
        (
            offset_y
            + GROUP_CARD_PADDING
            + (banner_h - GROUP_ICON_SIZE - GROUP_ICON_BORDER_WIDTH)
            + GROUP_ICON_BOTTOM_PLUS
        ),
    )
    image.draw_ellipse(
        (
            icon_x - GROUP_ICON_BORDER_WIDTH,
            icon_y - GROUP_ICON_BORDER_WIDTH,
            icon_x + GROUP_ICON_SIZE + GROUP_ICON_BORDER_WIDTH - 1,
            icon_y + GROUP_ICON_SIZE + GROUP_ICON_BORDER_WIDTH - 1,
        ),
        fill=GROUP_ICON_BORDER_COLOR,
    )
    image.paste(icon_img, (icon_x, icon_y), alpha=True)

    # title
    title_txt = get_fittable_text(
        group.name,
        GROUP_TITLE_TEXT_SIZE,
        card_w - (GROUP_CARD_PADDING * 2) - GROUP_TITLE_MARGIN_LEFT,
        fill=GROUP_TITLE_COLOR,
        weight="bold",
    )
    title_txt.draw_on_image(
        image.image,
        (
            offset_x + GROUP_CARD_PADDING + GROUP_TITLE_MARGIN_LEFT,
            (
                offset_y
                + GROUP_CARD_TOP_HEIGHT
                - GROUP_TITLE_MARGIN_BOTTOM
                - title_txt.height
            ),
        ),
    )

    # desc
    desc_txt = get_fittable_text(
        group.description.replace("\n", " "),
        GROUP_CONTENT_TEXT_SIZE,
        card_w - (GROUP_CARD_PADDING * 2),
        fill=GROUP_CONTENT_COLOR,
    )
    desc_h = (
        card_h - GROUP_CARD_TOP_HEIGHT - GROUP_CARD_PADDING * 3 - GROUP_FOOTER_HEIGHT
    )
    desc_y = (
        offset_y
        + GROUP_CARD_TOP_HEIGHT
        + GROUP_CARD_PADDING
        + ((desc_h - desc_txt.height) // 2)
    )
    desc_txt.draw_on_image(
        image.image,
        (
            offset_x + ((card_w - desc_txt.width) // 2),
            desc_y,
        ),
    )

    # footer
    footer_top_y = offset_y + card_h - GROUP_CARD_PADDING - GROUP_FOOTER_HEIGHT
    user_icon = BuildImage.open(BytesIO(USER_ICON_PATH.read_bytes()))
    user_icon_w, user_icon_h = user_icon.size
    image.paste(
        user_icon,
        (offset_x + GROUP_CARD_PADDING + GROUP_FOOTER_PADDING_LEFT, footer_top_y),
        alpha=True,
    )
    users_text = Text2Image.from_text(
        f" {group.member_count}",
        GROUP_CONTENT_TEXT_SIZE,
        fill=GROUP_CONTENT_COLOR,
    )
    users_text.draw_on_image(
        image.image,
        (
            offset_x + GROUP_CARD_PADDING + GROUP_FOOTER_PADDING_LEFT + user_icon_w,
            footer_top_y + ((user_icon_h - users_text.height) // 2),
        ),
    )
    code_text = Text2Image.from_text(
        f"{group.short_code}.{group.discriminator}",
        GROUP_CONTENT_TEXT_SIZE,
        fill=GROUP_CONTENT_COLOR,
    )
    code_text.draw_on_image(
        image.image,
        (
            (
                offset_x
                + card_w
                - GROUP_CARD_PADDING
                - GROUP_FOOTER_PADDING_LEFT
                - code_text.width
            ),
            footer_top_y + ((user_icon_h - code_text.height) // 2),
        ),
    )

    return image


async def draw_user_profile(user: "UserModel") -> BuildImage:
    bg = BuildImage.new("RGBA", (500, 500), BG_COLOR)
    bg.draw_text(
        (5, 5),
        f"User: {user.display_name}\nWorking in progress",
        fill=OVERVIEW_TITLE_COLOR,
    )
    return bg


# endregion
