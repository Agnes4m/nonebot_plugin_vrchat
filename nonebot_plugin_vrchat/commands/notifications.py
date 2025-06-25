import time
from typing import List

from loguru import logger
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot_plugin_alconna.uniseg import UniMessage
from vrchatapi import Notification

from ..message import draw_notification_card
from ..vrchat import (
    accept_friend_request,
    get_client,
    get_notifications,
    mark_notification_as_read,
)
from ..vrchat.notifications import delete_notification
from .utils import UserSessionId, handle_error, rule_enable, split_chinese_digits

logger.info(rule_enable)
show_notic = on_command(
    "vrcsn",
    aliases={"vrc显示通知", "vrc通知显示"},
    rule=rule_enable,
    priority=20,
)


@show_notic.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    state: T_State,
    arg: Message = CommandArg(),
):
    logger.debug(f"收到参数: {arg!r}")
    n = 60
    tag = arg.extract_plain_text().strip()
    start_time = time.perf_counter()
    if tag and tag.isdigit():
        num = int(tag)
        if 0 < num <= 100:
            n = tag
    try:
        client = await get_client(session_id)
        resp = await get_notifications(client, n=n)
    except Exception as e:
        await handle_error(matcher, e)
    logger.info(resp)
    if len(resp) == 0:
        await UniMessage.text("当前没用未读的通知").finish()
    state["notifications"] = resp
    state["client"] = client
    pic = await draw_notification_card(resp)
    if pic:
        logger.info("通知列表成功")

    end_time = time.perf_counter()
    logger.debug(f"通知 执行用时: {end_time - start_time:.3f} 秒")

    await (
        UniMessage.image(raw=pic)
        + UniMessage.text("输入图中标签按钮可以继续执行,0退出交互")
    ).send()
    await matcher.pause()


@show_notic.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    logger.debug(f"收到参数: {arg!r}")
    resp: List[Notification] = state["notifications"]
    args = arg.extract_plain_text().strip()
    if args == "0":
        await UniMessage.text("退出交互").finish()
    index, tag = await split_chinese_digits(args)
    logger.debug(f"收到参数: {index!r} |{tag}")
    ntf = resp[int(index) - 1]
    if ntf.type == "friendRequest":
        if tag == "接受":
            await accept_friend_request(state["client"], ntf.id)
            await UniMessage.text("已接受好友申请").finish()
        elif tag == "忽略":
            await mark_notification_as_read(state["client"], ntf.id)
            await UniMessage.text("已忽略好友申请").finish()
        elif tag == "拒绝":
            await delete_notification(state["client"], ntf.id)
            await UniMessage.text("已拒绝好友申请").finish()
        else:
            await UniMessage.text("无效操作好友申请").finish()
