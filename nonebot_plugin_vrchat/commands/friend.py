import time

from loguru import logger
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot_plugin_alconna.uniseg import UniMessage

from ..i18n import Lang
from ..message import draw_user_card_overview
from ..vrchat import get_all_friends, get_client
from .utils import UserSessionId, handle_error, rule_enable

friend_list = on_command(
    "vrcfl",
    aliases={"vrc全部好友", "vrc好友列表"},
    rule=rule_enable,
    priority=20,
)


@friend_list.handle()
async def _(matcher: Matcher, session_id: UserSessionId):

    start_time = time.perf_counter()
    try:
        client = await get_client(session_id)
        resp = [x async for x in get_all_friends(client)]
    except Exception as e:
        await handle_error(matcher, e)

    if not resp:
        await matcher.send(Lang.nbp_vrc.friend.empty_friend_list())

    pic = await draw_user_card_overview(resp, client=client)
    if pic:
        logger.info("绘制好友列表成功")

    end_time = time.perf_counter()
    logger.debug(f"好友 执行用时: {end_time - start_time:.3f} 秒")

    await UniMessage.image(raw=pic).finish()
