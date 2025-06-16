from nonebot import logger, on_command
from nonebot.matcher import Matcher
from nonebot_plugin_alconna.uniseg import UniMessage

from ..i18n import UserLocale
from ..message import draw_user_card_overview, i2b
from ..vrchat import get_all_friends, get_client
from .utils import UserSessionId, handle_error, rule_enable

matcher_lyric = on_command("歌词", aliases={"lrc", "lyric", "lyrics"})


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

    await UniMessage.image(raw=pic).finish()
