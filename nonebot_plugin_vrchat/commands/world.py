from nonebot import on_command
from nonebot.adapters import Message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, EventMessage, T_State
from nonebot_plugin_alconna import UniMessage
from vrchatapi import ApiClient
from vrchatapi.models import AddFavoriteRequest

from nonebot_plugin_vrchat.vrchat.favorites import add_favorite

from ..i18n import Lang
from ..message.world import draw_world_card_overview, draw_world_info
from ..vrchat import (
    LimitedWorldModel,
    add_favorite,
    get_or_random_client,
    get_world,
    search_worlds,
)
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
    await matcher.pause(
        "发送[1]查看第一个世界\n发送[喜好 1 world1]添加到喜好【world1】组\n发送[0]取消\n【可以用[vrc收藏组列表]指令来获取组",
    )


@search_world.handle()
async def _(matcher: Matcher, state: T_State, message: Message = EventMessage()):
    arg = message.extract_plain_text().strip()
    if arg == "0":
        await matcher.finish(Lang.nbp_vrc.general.discard_select())
    client: ApiClient = state[KEY_CLIENT]
    resp: list[LimitedWorldModel] = state[KEY_WORLD_RESP]

    # 查询详情部分 - 数字则获取单个世界信息输出
    if arg.isdigit():
        index = int(arg) - 1
        if index < 0 or index >= len(resp):
            await matcher.finish("无效的世界序号")
        world_id = resp[index].world_id
        world_detail = await get_world(client, world_id)
        msg = await draw_world_info(world_detail)
        await UniMessage.image(raw=msg).send()
        await matcher.finish()

    # 喜好操作部分 - 如果命令以"喜好"开头则添加收藏
    if arg.startswith("喜好"):
        parts = arg.replace("喜好", "").strip().split()
        if len(parts) < 2 or not parts[0].isdigit():
            await matcher.finish(
                "格式错误，发送[喜好 1 world1]添加到喜好【world1】组\n发送[0]取消\n【可以用[vrc收藏组列表]指令来获取组",
            )
        index = int(parts[0]) - 1
        if index < 0 or index >= len(resp):
            await matcher.finish("无效的世界序号")
        world_id = resp[index].world_id
        add_favorite_request = AddFavoriteRequest(
            type="world",
            favorite_id=world_id,
            tags=parts[1:],
        )
        result = await add_favorite(client, add_favorite_request)
        logger.info(f"已添加世界收藏：{world_id}, 结果：{result}")
        await matcher.finish(f"已成功添加世界 {resp[index].name} 到喜好")
