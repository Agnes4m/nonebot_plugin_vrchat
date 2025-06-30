from pathlib import Path
from typing import Callable, List, NoReturn, Type, Union
from typing_extensions import Annotated

import aiofiles
from nonebot.adapters import Message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, EventMessage
from nonebot_plugin_alconna import UniMessage
from nonebot_plugin_session import SessionId, SessionIdType
from vrchatapi import ApiClient, LimitedUser, Notification

from ..config import session_config
from ..i18n import Lang
from ..vrchat import (
    ApiException,
    LimitedUserModel,
    NotLoggedInError,
    UnauthorizedException,
)
from ..vrchat.notifications import (
    accept_friend_request,
    delete_notification,
    mark_notification_as_read,
)

try:
    import ujson as json
except ImportError:
    import json

UserSessionId = Annotated[str, SessionId(SessionIdType.USER, include_bot_id=False)]
GroupSessionId = Annotated[str, SessionId(SessionIdType.GROUP, include_bot_id=False)]


KEY_ARG = "arg"
KEY_CLIENT = "client"
KEY_LOGIN_INFO = "login_info"
KEY_OVERRIDE_LOGIN_INFO = "override_login_info"
KEY_USERNAME = "username"
KEY_PASSWORD = "password"
KEY_VERIFY_FUNC = "verify_func"
KEY_VERIFY_CODE = "verify_code"
KEY_CURRENT_USER = "current_user"
KEY_SEARCH_RESP = "search_resp"
KEY_NOTIF_RESP = "notif_resp"
KEY_WORLD_RESP = "world_resp"


async def rule_enable(group_id: GroupSessionId, user_id: UserSessionId) -> bool:
    return session_config.get(group_id, user_id)[0].enable


async def handle_error(matcher: Matcher, e: Exception) -> NoReturn:
    if isinstance(e, NotLoggedInError):
        await matcher.finish(Lang.nbp_vrc.login.not_logged_in())

    if isinstance(e, UnauthorizedException):
        logger.warning(f"UnauthorizedException: {e}")
        await matcher.finish(Lang.nbp_vrc.login.login_expired())

    if isinstance(e, ApiException):
        logger.error(f"Error when requesting api: [{e.status}] {e.reason}")
        await matcher.finish(
            Lang.nbp_vrc.general.server_error(status=e.status, reason=e.reason),
        )

    logger.exception("Exception when requesting api")
    await matcher.finish(Lang.nbp_vrc.general.unknown_error())


def register_arg_got_handlers(
    matcher: Type[Matcher],
    locale_getter: Callable[[Matcher], str],
    key: str = KEY_ARG,
):
    async def handler1(
        matcher: Matcher,
        arg: Message = CommandArg(),
    ):
        if arg.extract_plain_text().strip():
            matcher.set_arg(key, arg)
        else:
            await matcher.pause(locale_getter(matcher))

    async def handler2(matcher: Matcher, message: Message = EventMessage()):
        if key not in matcher.state:
            matcher.set_arg(key, message)

    matcher.append_handler(handler1)
    matcher.append_handler(handler2)


async def save_to_file(
    msg_id: str,
    msg: Union[LimitedUser, list[LimitedUser], dict, list],
    name: str = "msg_id",
):
    msg_path = Path(f"data/vrchat/{name}/") / f"{msg_id}.json"
    msg_path.parent.mkdir(parents=True, exist_ok=True)

    # 处理为json格式
    def to_dict(obj):
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
            return obj.dict()
        return obj

    data = [to_dict(x) for x in msg] if isinstance(msg, list) else to_dict(msg)

    async with aiofiles.open(msg_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=4))


async def read_to_file(msg_id: Union[str, int]) -> Union[dict, list, None]:

    msg_path = Path("data/vrchat/msg_id/") / f"{msg_id}.json"
    logger.debug(f"Reading message from {msg_path}")
    if not msg_path.exists():
        return None
    async with aiofiles.open(msg_path, "r", encoding="utf-8") as f:
        return json.loads(await f.read())


async def parse_index(arg: str, resp: List[LimitedUserModel], matcher: Matcher):
    """解析用户输入的序号，返回索引，异常时自动 reject."""
    arg = arg.strip()
    if not arg.isdigit():
        await matcher.reject(Lang.nbp_vrc.general.invalid_ordinal_format())
    index = int(arg) - 1
    if index < 0 or index >= len(resp):
        await matcher.reject(Lang.nbp_vrc.general.invalid_ordinal_range())
    return index


async def split_chinese_digits(s):
    """数字和文字分离"""
    if not s:
        return "", ""

    is_digit_start = s[0].isdigit()

    split_index = None
    for i in range(1, len(s)):
        if s[i].isdigit() != is_digit_start:
            split_index = i
            break

    if split_index is None:
        return (s, "") if is_digit_start else ("", s)
    part1 = s[:split_index]
    part2 = s[split_index:]
    return (part1, part2) if is_digit_start else (part2, part1)


async def process_notification(client: ApiClient, ntf: Notification, tag: str):
    if ntf.type == "friendRequest":
        if tag == Lang.nbp_vrc.notif.accept:
            await accept_friend_request(client, ntf.id)
            await UniMessage.text(Lang.nbp_vrc.notif.accept_resp).finish()
        elif tag == Lang.nbp_vrc.notif.ignore:
            await mark_notification_as_read(client, ntf.id)
            await UniMessage.text(Lang.nbp_vrc.notif.ignore_resp).finish()
        elif tag == Lang.nbp_vrc.notif.deny:
            await delete_notification(client, ntf.id)
            await UniMessage.text(Lang.nbp_vrc.notif.deny_resp).finish()
        else:
            await UniMessage.text(Lang.nbp_vrc.notif.error_handle).finish()
    else:
        await UniMessage.text(Lang.nbp_vrc.notif.error_handle).finish()
