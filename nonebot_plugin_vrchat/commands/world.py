from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText
from nonebot_plugin_alconna import UniMessage

from ..i18n import Lang
from ..vrchat import get_or_random_client, search_worlds
from .utils import (
    KEY_ARG,
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

    len_worlds = len(worlds)
    msg_factory = UniMessage.text(
        Lang.nbp_vrc.world.searched_world_tip(count=len_worlds),
    )
    for i, wld in enumerate(worlds, 1):
        msg_factory += UniMessage.image(wld.thumbnail_image_url)
        msg_factory += Lang.nbp_vrc.world.searched_world_info(
            index=i,
            name=wld.name,
            author=wld.author_name,
            created_at=wld.created_at,
        )
        if i != len_worlds:
            msg_factory += "\n-\n"

    await msg_factory.finish()
