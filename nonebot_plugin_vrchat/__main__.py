from nonebot import on_command
from nonebot.adapters import Event, Message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.typing import T_State

# from nonebot_plugin_saa import Image, MessageFactory, MessageSegmentFactory, Text
# from .config import config
from .utils import login_in
from .vrchat.friend import get_online_friends

login = on_command("vrcl", aliases={"vrc登录"}, priority=20)
friend_request = on_command("vrcfr", aliases={"vrc在线好友"}, priority=20)


@login.handle()
async def _(matcher: Matcher, tag: Message = CommandArg()):
    # username = config.vrc_username
    # password = config.vrc_password
    msg = tag.extract_plain_text()
    if msg:
        matcher.set_arg("login_msg", tag)


@login.got("login_msg", prompt="请输入登录账号密码，用空格间隔")
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
        await matcher.finish(f"登录成功，姓名为{msg}")
    if status == 500:
        await matcher.reject("参数或服务器错误")
    if status == 401:
        await matcher.send(msg)
    else:
        await matcher.finish("未知参数")


@login.got("a2f")
async def _(
    matcher: Matcher,
    event: Event,
    state: T_State,
):
    tag = str(state["a2f"])
    status, msg = await login_in(
        event.get_user_id(),
        state.get("username"),
        state.get("password"),
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


@friend_request.handle()
async def _(event: Event, matcher: Matcher):
    msg = await get_online_friends(event.get_user_id())
    await matcher.send(msg)
