from typing import Callable, NoReturn, Type

from nonebot.adapters import Message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, EventMessage

from ..config import session_config
from ..i18n import I18N, GroupSessionId, UserLocale, UserSessionId
from ..vrchat import ApiException, NotLoggedInError, UnauthorizedException

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


async def rule_enable(group_id: GroupSessionId, user_id: UserSessionId) -> bool:
    return session_config.get(group_id, user_id)[0].enable


async def handle_error(matcher: Matcher, i18n: I18N, e: Exception) -> NoReturn:
    if isinstance(e, NotLoggedInError):
        await matcher.finish(i18n.login.not_logged_in)

    if isinstance(e, UnauthorizedException):
        logger.warning(f"UnauthorizedException: {e}")
        await matcher.finish(i18n.login.login_expired)

    if isinstance(e, ApiException):
        logger.error(f"Error when requesting api: [{e.status}] {e.reason}")
        await matcher.finish(i18n.general.server_error.format(e.status, e.reason))

    logger.exception("Exception when requesting api")
    await matcher.finish(i18n.general.unknown_error)


def register_arg_got_handlers(
    matcher: Type[Matcher],
    locale_getter: Callable[[I18N], str],
    key: str = KEY_ARG,
):
    async def handler1(
        matcher: Matcher,
        i18n: UserLocale,
        arg: Message = CommandArg(),
    ):
        if arg.extract_plain_text().strip():
            matcher.set_arg(key, arg)
        else:
            await matcher.pause(locale_getter(i18n))

    async def handler2(matcher: Matcher, message: Message = EventMessage()):
        if key not in matcher.state:
            matcher.set_arg(key, message)

    matcher.append_handler(handler1)
    matcher.append_handler(handler2)
