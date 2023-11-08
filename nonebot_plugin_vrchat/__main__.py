from typing import Awaitable, Callable, List, NoReturn, Type

from nonebot import on_command
from nonebot.adapters import Event, Message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg, EventMessage
from nonebot.typing import T_State
from nonebot_plugin_saa import Image, MessageFactory, Text

from .config import env_config, session_config
from .draw import draw_user_card_overview, draw_user_profile, i2b
from .i18n import I18N, UserLocale, loaded_locales
from .utils import GroupSessionId, UserSessionId
from .vrchat import (
    ApiClient,
    ApiException,
    CurrentUser,
    LimitedUserModel,
    NotLoggedInError,
    TwoFactorAuthError,
    UnauthorizedException,
    get_all_friends,
    get_client,
    get_login_info,
    get_or_random_client,
    get_user,
    login_via_password,
    remove_login_info,
    search_users,
    search_worlds,
)

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


# region shared


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


async def rule_enable(group_id: GroupSessionId, user_id: UserSessionId) -> bool:
    return session_config.get(group_id, user_id)[0].enable


# endregion


# region help


vrc_help = on_command(
    "vrchelp",
    aliases={"vrc帮助"},
    rule=rule_enable,
    priority=20,
)


@vrc_help.handle()
async def _(matcher: Matcher, i18n: UserLocale):
    await matcher.finish(i18n.general.help)


# endregion


# region login


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
    i18n: UserLocale,
    arg_msg: Message = CommandArg(),
):
    try:
        login_info = get_login_info(session_id)
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
        await matcher.send(i18n.login.use_cached_login_info)
        return  # skip

    await matcher.pause(i18n.login.send_login_info)


@vrc_login.handle()
async def _(
    matcher: Matcher,
    event: Event,
    state: T_State,
    session_id: UserSessionId,
    i18n: UserLocale,
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
            await matcher.finish(i18n.login.discard_login)

        parsed = arg.split(" ")
        if len(parsed) != 2:
            await matcher.reject(i18n.login.invalid_info_format)
        username, password = parsed

    if KEY_OVERRIDE_LOGIN_INFO in state:
        await matcher.send(i18n.login.overwrite_login_info)

    try:
        current_user = await login_via_password(session_id, username, password)

    except TwoFactorAuthError as e:
        state[KEY_VERIFY_FUNC] = e.verify_func
        await matcher.pause(
            i18n.login.send_2fa_code.format(env_config.session_expire_timeout.seconds),
        )

    except ApiException as e:
        if e.status == 401:
            if KEY_USERNAME in state:
                del state[KEY_USERNAME]
            if KEY_PASSWORD in state:
                del state[KEY_PASSWORD]
            await matcher.reject(i18n.login.invalid_account)

        logger.error(f"Api error when logging in: [{e.status}] {e.reason}")
        remove_login_info(session_id)
        await matcher.finish(i18n.general.server_error.format(e.status, e.reason))

    except Exception:
        logger.exception("Exception when logging in")
        remove_login_info(session_id)
        await matcher.finish(i18n.general.unknown_error)

    state[KEY_CURRENT_USER] = current_user


@vrc_login.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    event: Event,
    session_id: UserSessionId,
    i18n: UserLocale,
):
    if KEY_CURRENT_USER in state:
        return  # skip

    verify_code = event.get_plaintext().strip()
    if not verify_code.isdigit():
        await matcher.reject(i18n.login.invalid_2fa_format)

    verify_func: Callable[[str], Awaitable[CurrentUser]] = state[KEY_VERIFY_FUNC]
    try:
        current_user = await verify_func(verify_code)

    except ApiException as e:
        if e.status == 401:
            await matcher.reject(i18n.login.invalid_2fa_code)

        logger.error(f"Api error when verifying 2FA code: [{e.status}] {e.reason}")
        remove_login_info(session_id)
        await matcher.finish(i18n.general.server_error.format(e.status, e.reason))

    except Exception:
        logger.exception("Exception when verifying 2FA code")
        remove_login_info(session_id)
        await matcher.finish(i18n.general.unknown_error)

    state[KEY_CURRENT_USER] = current_user


@vrc_login.handle()
async def _(matcher: Matcher, state: T_State, i18n: UserLocale):
    current_user: CurrentUser = state[KEY_CURRENT_USER]
    await matcher.finish(i18n.login.logged_in.format(current_user.display_name))


# endregion


# region friend


friend_list = on_command(
    "vrcfl",
    aliases={"vrcrq", "vrc全部好友", "vrc好友列表"},
    rule=rule_enable,
    priority=20,
)


@friend_list.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    i18n: UserLocale,
):
    try:
        client = await get_client(session_id)
        resp = [x async for x in get_all_friends(client)]
    except Exception as e:
        await handle_error(matcher, i18n, e)

    if not resp:
        await matcher.finish(i18n.friend.empty_friend_list)

    try:
        pic = i2b(await draw_user_card_overview(resp, client=client))
    except Exception as e:
        await handle_error(matcher, i18n, e)

    await MessageFactory(Image(pic)).finish()


# endregion


# region user


search_user = on_command(
    "vrcsu",
    aliases={"vrcus", "vrc查询用户"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(search_user, lambda i18n: i18n.user.send_user_name)


@search_user.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    session_id: UserSessionId,
    i18n: UserLocale,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject(i18n.general.empty_search_keyword)

    try:
        client = await get_or_random_client(session_id)
        resp = [x async for x in search_users(client, arg)]
    except Exception as e:
        await handle_error(matcher, i18n, e)

    if not resp:
        await matcher.finish(i18n.user.no_user_found)

    state[KEY_CLIENT] = client
    state[KEY_SEARCH_RESP] = resp
    # if len(resp) == 1:
    #     return  # skip

    try:
        resp = [x async for x in search_users(client, arg, max_size=10)]
        pic = i2b(await draw_user_card_overview(resp, group=False, client=client))
    except Exception as e:
        await handle_error(matcher, i18n, e)

    await MessageFactory(
        [
            Text(i18n.user.searched_user_tip.format(len(resp))),
            Image(pic),
        ],
    ).finish()  # .pause()


# TODO 没做完
@search_user.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    i18n: UserLocale,
    message: Message = EventMessage(),
):
    client: ApiClient = state[KEY_CLIENT]
    resp: List[LimitedUserModel] = state[KEY_SEARCH_RESP]

    if len(resp) == 1:
        index = 0
    else:
        arg = message.extract_plain_text().strip()
        if arg == "0":
            await matcher.finish(i18n.general.discard_select)

        if not arg.isdigit():
            await matcher.reject(i18n.general.invalid_ordinal_format)

        index = int(arg) - 1
        if not (0 <= index < len(resp)):
            await matcher.reject(i18n.general.invalid_ordinal_range)

    user_id = resp[index].user_id
    try:
        user = await get_user(client, user_id)
        pic = i2b(await draw_user_profile(user))
    except Exception as e:
        await handle_error(matcher, i18n, e)

    await MessageFactory(Image(pic)).finish()


# endregion


# region world


search_world = on_command(
    "vrcsw",
    aliases={"vrcws", "vrc查询世界"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(search_world, lambda i18n: i18n.world.send_world_name)


@search_world.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    i18n: UserLocale,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject(i18n.general.empty_search_keyword)

    try:
        client = await get_or_random_client(session_id)
        worlds = [x async for x in search_worlds(client, arg, max_size=10)]
    except Exception as e:
        await handle_error(matcher, i18n, e)

    if not worlds:
        await matcher.finish(i18n.world.no_world_found)

    len_worlds = len(worlds)
    msg_factory = MessageFactory(i18n.world.searched_world_tip.format(len_worlds))
    for i, wld in enumerate(worlds, 1):
        msg_factory += Image(wld.thumbnail_image_url)
        msg_factory += i18n.world.searched_world_info.format(
            i,
            wld.name,
            wld.author_name,
            wld.created_at,
        )
        if i != len_worlds:
            msg_factory += "\n-\n"

    await msg_factory.finish()


# endregion


# region locale


change_locale = on_command(
    "vrccl",
    aliases={"vrc切换语言"},
    rule=rule_enable,
    priority=20,
)


@change_locale.handle()
async def _(matcher: Matcher, i18n: UserLocale):
    locales = "\n".join(
        f"{i}. {v.metadata.name} ({k})"
        for i, (k, v) in enumerate(loaded_locales.items(), 1)
    )
    await matcher.pause(
        f"{i18n.locale.available_locales_tip}\n"
        f"{locales}\n"
        f"{i18n.locale.select_locale_tip}",
    )


@change_locale.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    i18n: UserLocale,
    message: Message = EventMessage(),
):
    arg = message.extract_plain_text().strip()
    if not arg:
        await matcher.reject(i18n.general.empty_message)

    if arg == "0":
        await matcher.finish(i18n.general.discard_select)

    if not arg.isdigit():
        await matcher.reject(i18n.general.invalid_ordinal_format)

    index = int(arg) - 1
    if not (0 <= index < len(loaded_locales)):
        await matcher.reject(i18n.general.invalid_ordinal_range)

    name, i18n = list(loaded_locales.items())[index]
    config = session_config.get(session_id)[0].copy(update={"locale": name})
    session_config[session_id] = config

    await matcher.finish(
        i18n.locale.locale_changed.format(
            i18n.metadata.name,
            name,
            i18n.metadata.author,
        ),
    )
