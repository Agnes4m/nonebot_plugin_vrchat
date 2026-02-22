import time

from nonebot import on_command
from nonebot.log import logger
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
    logger.debug("开始处理好友列表请求")

    try:
        client = await get_client(session_id)

        resp = [x async for x in get_all_friends(client)]
    except Exception as e:
        logger.error(f"获取好友列表时发生错误: {e}")
        await handle_error(matcher, e)

    if not resp:
        logger.debug("好友列表为空")
        await matcher.send(Lang.nbp_vrc.friend.empty_friend_list())

    logger.debug("开始绘制好友列表图片")
    pic_start_time = time.perf_counter()
    pic = await draw_user_card_overview(resp, client=client)
    pic_end_time = time.perf_counter()
    logger.debug(f"图片绘制完成，用时: {pic_end_time - pic_start_time:.3f} 秒")

    if pic:
        logger.info("绘制好友列表成功")

    end_time = time.perf_counter()
    total_time = end_time - start_time
    logger.info(f"好友列表命令执行完成，总用时: {total_time:.3f} 秒")

    await UniMessage.image(raw=pic).finish()
