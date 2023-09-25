from nonebot import on_command
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText
from nonebot.typing import T_State

# from nonebot_plugin_saa import Image, MessageFactory, MessageSegmentFactory, Text
# from .config import config
from .utils import login_in

login = on_command("login", aliases={"登录vrc"}, priority=20)


# @login.handle()
# async def _(matcher: Matcher):
#     # username = config.vrc_username
#     # password = config.vrc_password
#     if config.vrc_username and config.vrc_password:
#         matcher.set_arg("login_msg", f"{config.vrc_username} {config.vrc_password}")


@login.got("login_msg", prompt="请输入登录账号密码，用空格间隔")
async def _(
    matcher: Matcher,
    event: Event,
    state: T_State,
    tag: str = ArgPlainText("login_msg"),
):
    try:
        username, password = tag.split(" ")
        state["username"] = username
        state["password"] = password
    except Exception:
        await matcher.finish("格式不符合规范,请重来")
    status, msg = await login_in(event.get_user_id(), username, password)
    if status == 200:
        await matcher.finish("登录成功，姓名为{msg}")
    if status == 500:
        await matcher.finish("参数或服务器错误")
    if status == 401:
        matcher.set_arg("a2f", msg)


@login.got("a2f", prompt="请输入邮箱验证码")
async def _(
    matcher: Matcher,
    event: Event,
    state: T_State,
    tag: str = ArgPlainText("a2f"),
):
    status, msg = await login_in(
        event.get_user_id(),
        state.get("username"),
        state.get("password"),
        code=tag,
    )
    if not tag.isdigit():
        await matcher.finish("输入的不是验证码拉")
    if status == 200:
        await matcher.finish(f"登录成功，姓名为{msg}")
    if status == 500:
        await matcher.send(f"参数或服务器错误:{msg}")
    if status == 401:
        matcher.receive("验证码错误,重新输入")
