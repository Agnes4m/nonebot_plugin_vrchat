import time
from typing import List

from loguru import logger
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, EventMessage
from nonebot.typing import T_State
from nonebot_plugin_alconna.uniseg import UniMessage
from vrchatapi import ApiClient, Notification
from vrchatapi.exceptions import NotFoundException

from ..i18n.model import Lang
from ..message import draw_notification_card
from ..vrchat import (
    accept_friend_request,
    get_client,
    get_notifications,
    mark_notification_as_read,
)
from ..vrchat.notifications import delete_notification
from .utils import (
    KEY_CLIENT,
    KEY_NOTIF_RESP,
    UserSessionId,
    handle_error,
    rule_enable,
    split_chinese_digits,
)

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
    logger.debug(resp)
    if len(resp) == 0:
        await UniMessage.text(Lang.nbp_vrc.notif.no_request).finish()
    state[KEY_NOTIF_RESP] = resp
    state[KEY_CLIENT] = client
    pic = await draw_notification_card(resp)
    if pic:
        logger.info("通知列表成功")

    end_time = time.perf_counter()
    logger.debug(f"通知 执行用时: {end_time - start_time:.3f} 秒")

    await (
        UniMessage.image(raw=pic) + UniMessage.text(Lang.nbp_vrc.notif.reply_notif)
    ).send()
    await matcher.pause()


@show_notic.handle()
async def _(matcher: Matcher, state: T_State, message: Message = EventMessage()):
    client: ApiClient = state[KEY_CLIENT]
    resp: List[Notification] = state[KEY_NOTIF_RESP]
    arg = message.extract_plain_text().strip()

    logger.debug(f"收到参数: {arg!r}")

    index, tag = await split_chinese_digits(arg)
    if index == "0":
        await UniMessage.text("退出交互").finish()
    logger.debug(f"收到参数: {index!r} |{tag}")
    ntf = resp[int(index) - 1]
    try:
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
    except NotFoundException as e:
        if e.status == 404:
            await UniMessage.text(Lang.nbp_vrc.notif.processed).finish()
        else:
            await handle_error(matcher, e)
