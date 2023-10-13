from typing import Awaitable, Callable, List, NoReturn

from nonebot import on_command
from nonebot.adapters import Event, Message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.typing import T_State
from nonebot_plugin_saa import Image, MessageFactory, Text
from nonebot_plugin_session import SessionId, SessionIdType
from vrchatapi import ApiClient, CurrentUser

from .config import config
from .draw import draw_user_card_overview, draw_user_profile, i2b
from .vrchat import (
    ApiException,
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

HELP = """--------vrc指令--------
1、【vrc登录】 | 登录vrc账户，建议私聊
2、【vrc全部好友】 | 获取全部好友信息
3、【vrc查询用户】【text】 | 查询玩家
4、【vrc查询世界】【text】 | 查询世界"""

vrc_help = on_command("vrchelp", aliases={"vrc帮助"}, priority=20)
vrc_login = on_command("vrcl", aliases={"vrc登录"}, priority=20)
friend_request = on_command("vrcrq", aliases={"vrc全部好友"}, priority=20)
search_user = on_command("vrcsu", aliases={"vrc查询用户"}, priority=20)
world_search = on_command("vrcws", aliases={"vrc查询世界"}, priority=20)


async def handle_error(matcher: Matcher, e: Exception) -> NoReturn:
    if isinstance(e, NotLoggedInError):
        await matcher.finish("尚未登录，请私聊并发送【vrc登录】")

    if isinstance(e, UnauthorizedException):
        logger.warning(f"UnauthorizedException: {e}")
        await matcher.finish("登录已过期，请重新登录")

    if isinstance(e, ApiException):
        logger.error(f"Error when requesting api: [{e.status}] {e.reason}")
        await matcher.finish(f"服务器返回异常：[{e.status}] {e.reason}")

    logger.exception("Exception when requesting api")
    await matcher.finish("遇到未知错误，请检查后台输出")


@vrc_help.handle()
async def _(matcher: Matcher):
    await matcher.finish(HELP)


@vrc_login.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    session_id: str = SessionId(SessionIdType.USER),
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
        await matcher.send("检测到缓存的登录信息，尝试重新登录")
        return  # skip

    await matcher.pause("请发送登录账号密码，用空格分隔，发送 0 取消登录\n提示：机器人会保存你的登录状态,请在信任机器人的情况下登录")


@vrc_login.handle()
async def _(
    matcher: Matcher,
    event: Event,
    state: T_State,
    session_id: str = SessionId(SessionIdType.USER),
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
            await matcher.finish("已取消登录")

        parsed = arg.split(" ")
        if len(parsed) != 2:
            await matcher.reject("消息格式不符合规范，请重新发送账号密码，用空格分隔")
        username, password = parsed

    if KEY_OVERRIDE_LOGIN_INFO in state:
        await matcher.send("检测到已缓存的登录信息，本次登录成功后旧登录信息将被覆盖")

    try:
        current_user = await login_via_password(session_id, username, password)

    except TwoFactorAuthError as e:
        state[KEY_VERIFY_FUNC] = e.verify_func
        secs = config.session_expire_timeout.seconds
        await matcher.pause(f"请在 {secs} 秒内发送 收到的邮箱验证码 或者 2FA验证码")

    except ApiException as e:
        if e.status == 401:
            if KEY_USERNAME in state:
                del state[KEY_USERNAME]
            if KEY_PASSWORD in state:
                del state[KEY_PASSWORD]
            await matcher.reject("用户名或密码错误，请重新发送")

        logger.error(f"Api error when logging in: [{e.status}] {e.reason}")
        remove_login_info(session_id)
        await matcher.finish(f"服务器返回异常：[{e.status}] {e.reason}")

    except Exception:
        logger.exception("Exception when logging in")
        remove_login_info(session_id)
        await matcher.finish("遇到未知错误，请检查后台输出")

    state[KEY_CURRENT_USER] = current_user


@vrc_login.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    event: Event,
    session_id: str = SessionId(SessionIdType.USER),
):
    if KEY_CURRENT_USER in state:
        return  # skip

    verify_code = event.get_plaintext().strip()
    if not verify_code.isdigit():
        await matcher.reject("验证码格式不正确")

    verify_func: Callable[[str], Awaitable[CurrentUser]] = state[KEY_VERIFY_FUNC]
    try:
        current_user = await verify_func(verify_code)

    except ApiException as e:
        if e.status == 401:
            await matcher.reject("验证码错误，请重新发送")

        logger.error(f"Api error when verifying 2FA code: [{e.status}] {e.reason}")
        remove_login_info(session_id)
        await matcher.finish(f"服务器返回异常：[{e.status}] {e.reason}")

    except Exception:
        logger.exception("Exception when verifying 2FA code")
        remove_login_info(session_id)
        await matcher.finish("遇到未知错误，请检查后台输出")

    state[KEY_CURRENT_USER] = current_user


@vrc_login.handle()
async def _(matcher: Matcher, state: T_State):
    current_user: CurrentUser = state[KEY_CURRENT_USER]
    await matcher.finish(f"登录成功，欢迎，{current_user.display_name}")


@friend_request.handle()
async def _(
    matcher: Matcher,
    session_id: str = SessionId(SessionIdType.USER),
):
    try:
        client = get_client(session_id)
        resp = [x async for x in get_all_friends(client)]
    except Exception as e:
        await handle_error(matcher, e)

    if not resp:
        await matcher.finish("当前没有好友捏")

    try:
        pic = i2b(await draw_user_card_overview(resp))
    except Exception as e:
        await handle_error(matcher, e)

    await MessageFactory(Image(pic)).finish()


@search_user.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        matcher.set_arg(KEY_ARG, arg)


@search_user.got(KEY_ARG, prompt="请发送要查询的玩家名称")
async def _(
    matcher: Matcher,
    state: T_State,
    arg: str = ArgPlainText(KEY_ARG),
    session_id: str = SessionId(SessionIdType.USER),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("搜索关键词不能为空，请重新发送")

    try:
        client = get_or_random_client(session_id)
        resp = [x async for x in search_users(client, arg)]
    except Exception as e:
        await handle_error(matcher, e)

    if not resp:
        await matcher.finish("没搜到任何玩家捏")

    state[KEY_CLIENT] = client
    state[KEY_SEARCH_RESP] = resp
    # if len(resp) == 1:
    #     return  # skip

    try:
        resp = [x async for x in search_users(client, arg)]
        resp = resp[::20]
        pic = i2b(await draw_user_card_overview(resp, group=False))
    except Exception as e:
        await handle_error(matcher, e)

    await MessageFactory(
        [
            Text(f"搜索到以下 {len(resp)} 个玩家"),
            # Text(f"搜索到以下 {len(resp)} 个玩家，发送序号查看玩家详情，发送 0 取消选择"),
            Image(pic),
        ],
    ).finish()  # .pause()


# TODO 没做完
@search_user.handle()
async def _(matcher: Matcher, state: T_State, event: Event):
    client: ApiClient = state[KEY_CLIENT]
    resp: List[LimitedUserModel] = state[KEY_SEARCH_RESP]

    if len(resp) == 1:
        index = 0
    else:
        arg = event.get_plaintext().strip()
        if arg == "0":
            await matcher.finish("已取消选择")

        if not arg.isdigit():
            await matcher.reject("序号格式不正确，请重新发送")

        index = int(arg) - 1
        if not (0 <= index < len(resp)):
            await matcher.reject("序号不在范围内，请重新发送")

    user_id = resp[index].user_id
    try:
        user = await get_user(client, user_id)
        pic = i2b(await draw_user_profile(user))
    except Exception as e:
        await handle_error(matcher, e)

    await MessageFactory(Image(pic)).finish()


@world_search.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        matcher.set_arg(KEY_ARG, arg)


@world_search.got(KEY_ARG, prompt="请发送要查询的地图名称")
async def _(
    matcher: Matcher,
    arg: str = ArgPlainText(KEY_ARG),
    session_id: str = SessionId(SessionIdType.USER),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("搜索关键词不能为空，请重新发送")

    try:
        client = get_or_random_client(session_id)
        worlds = [x async for x in search_worlds(client, arg)]
    except Exception as e:
        await handle_error(matcher, e)

    if not worlds:
        await matcher.finish("没搜到任何地图捏")

    msg_factory = MessageFactory("搜索到以下地图")
    for wld in worlds:
        if isinstance(wld.thumbnail_image_url, str):
            msg_factory += Image(wld.thumbnail_image_url)
            msg_factory += (
                f"名称：{wld.name}\n作者：{wld.author_name}\n创建日期：{wld.created_at}\n-\n",
            )
    await msg_factory.finish()
