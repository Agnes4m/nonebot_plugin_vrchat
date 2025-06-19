from typing import Awaitable, Callable

from nonebot import on_command
from nonebot.adapters import Event, Message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.typing import T_State

from ..config import env_config
from ..i18n import Lang
from ..vrchat import (
    ApiException,
    CurrentUser,
    NotLoggedInError,
    TwoFactorAuthError,
    get_login_info,
    login_via_password,
    remove_login_info,
)
from .utils import (
    KEY_CURRENT_USER,
    KEY_LOGIN_INFO,
    KEY_OVERRIDE_LOGIN_INFO,
    KEY_PASSWORD,
    KEY_USERNAME,
    KEY_VERIFY_FUNC,
    UserSessionId,
    rule_enable,
)

vrc_login = on_command(
    "vrcl",
    aliases={"vrc登录"},
    rule=rule_enable,
    priority=20,
)


@vrc_login.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    session_id: UserSessionId,
    arg_msg: Message = CommandArg(),
):
    """
    异步处理登录请求。

    Args:
        matcher (Matcher): 用于匹配用户输入的匹配器对象。
        state (T_State): 用于保存处理状态的对象。
        session_id (UserSessionId): 用户会话ID。
        i18n (UserLocale): 用户语言环境。
        arg_msg (Message, optional): 用户输入的命令参数消息，默认为 CommandArg().

    Returns:
        None

    Raises:
        NotLoggedInError: 如果用户未登录则抛出此异常。
    """
    try:
        login_info = get_login_info(session_id)
        logger.info(f"login_info: {login_info}")
    except NotLoggedInError:
        login_info = None

    if arg_msg.extract_plain_text().strip():
        if login_info:
            state[KEY_OVERRIDE_LOGIN_INFO] = True
        matcher.set_arg(KEY_LOGIN_INFO, arg_msg)
        return  # skip

    # no arg
    if login_info:
        state[KEY_USERNAME] = login_info.username
        state[KEY_PASSWORD] = login_info.password
        await matcher.send(Lang.nbp_vrc.login.use_cached_login_info())
        return  # skip

    await matcher.pause(Lang.nbp_vrc.login.send_login_info())


@vrc_login.handle()
async def _(
    matcher: Matcher,
    event: Event,
    state: T_State,
    session_id: UserSessionId,
):
    if (KEY_USERNAME in state) and (KEY_PASSWORD in state):
        username: str = state[KEY_USERNAME]
        password: str = state[KEY_PASSWORD]
    else:
        if KEY_LOGIN_INFO in state:
            arg_msg: Message = state[KEY_LOGIN_INFO]
            del state[KEY_LOGIN_INFO]
            arg = arg_msg.extract_plain_text()
        else:
            arg = event.get_plaintext()

        arg = arg.strip()
        if arg == "0":
            await matcher.finish(Lang.nbp_vrc.login.discard_login())

        parsed = arg.split(" ")
        if len(parsed) != 2:
            await matcher.reject(Lang.nbp_vrc.login.invalid_info_format())
        username, password = parsed

    if KEY_OVERRIDE_LOGIN_INFO in state:
        await matcher.send(Lang.nbp_vrc.login.overwrite_login_info())

    try:
        current_user = await login_via_password(session_id, username, password)

    except TwoFactorAuthError as e:
        state[KEY_VERIFY_FUNC] = e.verify_func
        await matcher.pause(
            Lang.nbp_vrc.login.send_2fa_code(
                second=env_config.session_expire_timeout.seconds,
            ),
        )

    except ApiException as e:
        if e.status == 401:
            if KEY_USERNAME in state:
                del state[KEY_USERNAME]
            if KEY_PASSWORD in state:
                del state[KEY_PASSWORD]
            await matcher.reject(Lang.nbp_vrc.login.invalid_account())

        logger.error(f"Api error when logging in: [{e.status}] {e.reason}")
        remove_login_info(session_id)
        await matcher.finish(
            Lang.nbp_vrc.general.server_error(status=e.status, reason=e.reason),
        )

    except Exception:
        logger.exception("Exception when logging in")
        remove_login_info(session_id)
        await matcher.finish(Lang.nbp_vrc.general.unknown_error())

    state[KEY_CURRENT_USER] = current_user


@vrc_login.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    event: Event,
    session_id: UserSessionId,
):
    if KEY_CURRENT_USER in state:
        return  # skip

    verify_code = event.get_plaintext().strip()
    if not verify_code.isdigit():
        await matcher.reject(Lang.nbp_vrc.login.invalid_2fa_format())

    verify_func: Callable[[str], Awaitable[CurrentUser]] = state[KEY_VERIFY_FUNC]
    try:
        current_user = await verify_func(verify_code)

    except ApiException as e:
        if e.status == 401:
            await matcher.reject(Lang.nbp_vrc.login.invalid_2fa_code())

        logger.error(f"Api error when verifying 2FA code: [{e.status}] {e.reason}")
        remove_login_info(session_id)
        await matcher.finish(
            Lang.nbp_vrc.general.server_error(status=e.status, reason=e.reason),
        )

    except Exception:
        logger.exception("Exception when verifying 2FA code")
        remove_login_info(session_id)
        await matcher.finish(Lang.nbp_vrc.general.unknown_error())

    state[KEY_CURRENT_USER] = current_user


@vrc_login.handle()
async def _(matcher: Matcher, state: T_State):
    current_user: CurrentUser = state[KEY_CURRENT_USER]
    state[KEY_CURRENT_USER] = current_user
    await matcher.finish(
        Lang.nbp_vrc.login.logged_in(name=current_user.display_name),
    )
