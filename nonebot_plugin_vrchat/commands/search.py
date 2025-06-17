from typing import List

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, EventMessage
from nonebot.typing import T_State
from nonebot_plugin_alconna import UniMessage

from ..i18n import Lang
from ..message import draw_user_card_overview, draw_user_profile_card
from ..vrchat import (
    ApiClient,
    LimitedUserModel,
    get_or_random_client,
    get_user,
    search_users,
)
from .utils import (
    KEY_ARG,
    KEY_CLIENT,
    KEY_SEARCH_RESP,
    UserSessionId,
    handle_error,
    register_arg_got_handlers,
    rule_enable,
)

search_user = on_command(
    "vrcsu",
    aliases={"vrcus", "vrc搜索用户"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    search_user,
    lambda matcher: Lang.nbp_vrc.user.send_user_name(),  # noqa: ARG005
)


@search_user.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject(Lang.nbp_vrc.general.empty_search_keyword())

    try:
        client = await get_or_random_client(session_id)
        resp = [x async for x in search_users(client, arg)]
    except Exception as e:
        await handle_error(matcher, e)

    if not resp:
        await matcher.finish(Lang.nbp_vrc.user.no_user_found())

    state[KEY_CLIENT] = client
    state[KEY_SEARCH_RESP] = resp
    # if len(resp) == 1:
    #     return  # skip

    try:
        resp = [x async for x in search_users(client, arg, max_size=10)]
        pic = await draw_user_card_overview(
            resp,
            group=False,
            client=client,
            title="搜索结果",
        )
    except Exception as e:
        await handle_error(matcher, e)

    await (
        UniMessage.text(Lang.nbp_vrc.user.searched_user_tip(count=len(resp)))
        + UniMessage.image(raw=pic)
    ).send()
    # 进入多步会话，等待用户选择
    await matcher.pause("请选择要查询的用户序号：\n输入 0 取消选择\n")


@search_user.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    message: Message = EventMessage(),
):
    client: ApiClient = state[KEY_CLIENT]
    resp: List[LimitedUserModel] = state[KEY_SEARCH_RESP]

    if len(resp) == 1:
        index = 0
    else:
        arg = message.extract_plain_text().strip()
        if arg == "0":
            await matcher.finish(Lang.nbp_vrc.general.discard_select())

        if not arg.isdigit():
            await matcher.reject(Lang.nbp_vrc.general.invalid_ordinal_format())

        index = int(arg) - 1
        if index < 0 or index >= len(resp):
            await matcher.reject(Lang.nbp_vrc.general.invalid_ordinal_range())

    user_id = resp[index].user_id
    try:
        user = await get_user(client, user_id)
        pic = await draw_user_profile_card(user)
    except Exception as e:
        await handle_error(matcher, e)

    await UniMessage.image(raw=pic).finish()
