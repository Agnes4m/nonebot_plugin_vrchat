import time

from loguru import logger
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot_plugin_alconna.uniseg import UniMessage

from ..message import draw_notification_card
from ..vrchat import get_client, get_notifications
from .utils import UserSessionId, handle_error, rule_enable

logger.info(rule_enable)
show_notic = on_command(
    "vrcsn",
    aliases={"vrc显示通知", "vrc通知显示"},
    rule=rule_enable,
    priority=20,
)


@show_notic.handle()
async def _(matcher: Matcher, session_id: UserSessionId, arg: Message = CommandArg()):
    logger.debug(f"收到参数: {arg!r}")
    n = 60
    tag = arg.extract_plain_text().strip()
    start_time = time.perf_counter()
    if tag and tag.isdigit():
        num = int(tag)
        if 0 < num <= 100:
            n = tag
        else:
            await matcher.finish("数字应为0-100")
    try:
        client = await get_client(session_id)
        resp = await get_notifications(client, n=n)
    except Exception as e:
        await handle_error(matcher, e)
    logger.debug(resp)
    pic = await draw_notification_card(resp, client=client)
    if pic:
        logger.info("通知列表成功")

    end_time = time.perf_counter()
    logger.debug(f"通知 执行用时: {end_time - start_time:.3f} 秒")

    await UniMessage.image(raw=pic).finish()
