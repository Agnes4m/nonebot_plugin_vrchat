from nonebot import on_command
from nonebot.adapters import Event, Message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.typing import T_State
from nonebot_plugin_saa import Image, MessageFactory
from vrchatapi.exceptions import UnauthorizedException

from .draw import draw_user_card_overview, i2b, transform_limited_users
from .vrchat.friend import get_all_friends
from .vrchat.login import login_in
from .vrchat.users import search_users
from .vrchat.world import worlds_search

vrc_help = on_command("vrchelp", aliases={"vrc帮助"}, priority=20)
vrc_login = on_command("vrcl", aliases={"vrc登录"}, priority=20)
# friend_online = on_command("vrcol", aliases={"vrc在线好友"}, priority=20)
friend_request = on_command("vrcrq", aliases={"vrc全部好友"}, priority=20)
search_user = on_command("vrcsu", aliases={"vrc查询用户"}, priority=20)
world_search = on_command("vrcws", aliases={"vrc查询世界"}, priority=20)


@vrc_help.handle()
async def _(matcher: Matcher):
    help_msg = """--------vrc指令--------
    1、【vrc登录】 | 登录vrc账户，建议私聊
    2、【vrc全部好友】 | 获取全部好友信息
    3、【vrc查询用户】【text】 | 查询玩家
    4、【vrc查询世界】【text】 | 查询世界
    """
    await matcher.finish(help_msg)


@vrc_login.handle()
async def _(matcher: Matcher, tag: Message = CommandArg()):
    # username = config.vrc_username
    # password = config.vrc_password
    msg = tag.extract_plain_text()
    if msg:
        matcher.set_arg("login_msg", tag)


@vrc_login.got("login_msg", prompt="请输入登录账号密码，用空格间隔\n提示:机器人会保存你的登录状态,请在信任机器人的情况下登录")
async def _(
    matcher: Matcher,
    event: Event,
    state: T_State,
    tag: str = ArgPlainText("login_msg"),
):
    logger.info("参数" + tag)
    print("参数" + tag)
    try:
        username, password = tag.split(" ")
        state["username"] = username
        state["password"] = password
    except Exception:
        await matcher.finish("格式不符合规范,请重来")
    print(username, password)
    status, msg = await login_in(event.get_user_id(), username, password)
    if status == 200:
        await matcher.finish(f"登录成功，欢迎，{msg}")
    if status == 500:
        await matcher.reject("参数或服务器错误")
    if status == 401:
        await matcher.send(msg)
    else:
        await matcher.finish("未知参数")


@vrc_login.got("a2f")
async def _(
    matcher: Matcher,
    event: Event,
    state: T_State,
):
    tag = str(state["a2f"])
    status, msg = await login_in(
        event.get_user_id(),
        state.get("username"),  # type: ignore
        state.get("password"),  # type: ignore
        code=tag,
    )
    logger.info(state.get("username"))
    logger.info(state.get("password"))
    logger.info(tag)
    if not tag.isdigit():
        await matcher.finish("输入的不是验证码拉")
    if status == 200:
        await matcher.finish(f"登录成功，姓名为{msg}")
    if status == 500:
        await matcher.send(f"参数或服务器错误:{msg}")
    if status == 401:
        matcher.receive("验证码错误,重新输入")


# @friend_online.handle()
# async def _(event: Event, matcher: Matcher):
#     msg = await get_all_friends(event.get_user_id())
#     if msg is None:
#         await matcher.finish("尚未登录,请私聊并发送【vrc登录】")
#     if msg:
#         send_msg = await friend_status_msg(msg)
#         if send_msg:
#             num = (len(send_msg) + 1) // 2 if len(send_msg) != 0 else 0
#             send_msg.insert(0, f"当前在线好友数量 {num} / {len(msg)}")
#             await MessageFactory(send_msg).finish()
#     await matcher.finish("当前没有好友捏")


@friend_request.handle()
async def _(event: Event, matcher: Matcher):
    try:
        msg = await get_all_friends(event.get_user_id())
    except UnauthorizedException as e:
        logger.warning(f"UnauthorizedException: {e}")
        await matcher.finish("登录已过期，请重新登录")
    except Exception:
        logger.exception("Exception when getting friends")
        await matcher.finish("请求失败，请检查后台输出")

    if msg is None:
        await matcher.finish("尚未登录,请私聊并发送【vrc登录】")
    if msg:
        usr = transform_limited_users(msg)
        send_msg = i2b(await draw_user_card_overview(usr))
        await MessageFactory([Image(send_msg)]).finish()
        # send_msg = await friend_status_msg(msg)
        # if send_msg:
        #     send_msg.insert(0, f"好友数量 {len(msg)}")
        #     await MessageFactory(send_msg).finish()
    await matcher.finish("当前没有好友捏")


@search_user.handle()
async def _(event: Event, matcher: Matcher, arg: Message = CommandArg()):
    msg = await search_users(event.get_user_id(), arg.extract_plain_text())
    if msg is not None:
        usr = transform_limited_users(msg)
        send_msg = i2b(await draw_user_card_overview(usr))
        await MessageFactory([Image(send_msg)]).finish()
        # send_msg = await search_usrs_msg(msg)
        # if send_msg:
        #     send_msg.insert(0, f"查询玩家数量 {len(msg)}")
        #     await MessageFactory(send_msg).finish()
    await matcher.finish("没有这个玩家")


@world_search.handle()
async def _(event: Event, matcher: Matcher, arg: Message = CommandArg()):
    msg = await worlds_search(event.get_user_id(), arg.extract_plain_text())
    if msg is not None:
        print(msg)
        send_msg: list = ["搜索到以下地图"]
        # send_msg = await draw_and_save(msg)
        # send_msg = await search_usrs_msg(msg)
        for one in msg:
            if isinstance(one.thumbnail_image_url, str):
                send_msg.append(Image(one.thumbnail_image_url))
                send_msg.append(
                    f"""名称:{one.name}
                    作者：{one.author_name}
                    创建日期：{one.created_at}            
                    """,
                )

    await matcher.finish("没有这个地图")
