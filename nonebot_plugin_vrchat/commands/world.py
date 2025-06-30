from nonebot import on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, EventMessage, T_State
from nonebot_plugin_alconna import UniMessage
from vrchatapi import ApiClient

from ..i18n import Lang
from ..message.world import draw_world_card_overview
from ..vrchat import LimitedWorldModel, get_or_random_client, get_world, search_worlds
from .utils import (
    KEY_ARG,
    KEY_CLIENT,
    KEY_WORLD_RESP,
    UserSessionId,
    handle_error,
    register_arg_got_handlers,
    rule_enable,
)

search_world = on_command(
    "vrcsw",
    aliases={"vrcws", "vrc搜索世界"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    search_world,
    lambda matcher: Lang.nbp_vrc.world.send_world_name(),  # noqa: ARG005
)


@search_world.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    state: T_State,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject(Lang.nbp_vrc.general.empty_search_keyword())

    try:
        client, _ = await get_or_random_client(session_id)
        worlds = [x async for x in search_worlds(client, arg, max_size=10)]
    except Exception as e:
        await handle_error(matcher, e)

    if not worlds:
        await matcher.finish(Lang.nbp_vrc.world.no_world_found())
    state[KEY_WORLD_RESP] = worlds
    state[KEY_CLIENT] = client
    msg = await draw_world_card_overview(worlds)
    await UniMessage.image(raw=msg).send()
    await matcher.pause("发送[1]查看第一个世界\n发送[喜好 1]添加到喜好\n发送[0]取消")


@search_world.handle()
async def _(matcher: Matcher, state: T_State, message: Message = EventMessage()):
    arg = message.extract_plain_text().strip()
    if arg == "0":
        await matcher.finish(Lang.nbp_vrc.general.discard_select())
    client: ApiClient = state[KEY_CLIENT]
    resp: list[LimitedWorldModel] = state[KEY_WORLD_RESP]

    # 查询详情部分
    if arg.isdigit():
        world = resp[int(arg) - 1]
        print(type(world))
        worlds = await get_world(client, resp[int(arg) - 1].world_id)
        print(worlds)
    if arg.startswith("喜好"):
        index = int(arg.split(" ", 1)[1])
        world = resp[index - 1]
        worlds = await get_world(client, resp[index - 1].world_id)
        print(worlds)
