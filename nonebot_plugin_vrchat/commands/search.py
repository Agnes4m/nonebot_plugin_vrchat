import time
from typing import List

from loguru import logger
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, EventMessage
from nonebot.typing import T_State
from nonebot_plugin_alconna import UniMessage
from vrchatapi import ApiException

from ..i18n import Lang
from ..message import draw_user_card_overview, draw_user_profile_card
from ..vrchat import (
    ApiClient,
    LimitedUserModel,
    friend,
    get_friend_status,
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
    parse_index,
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
    start_time = time.perf_counter()
    if not arg:
        await matcher.reject(Lang.nbp_vrc.general.empty_search_keyword())
    logger.info(f"正在查询{arg}")
    try:
        client, is_me = await get_or_random_client(session_id)
        resp = [x async for x in search_users(client, arg, max_size=10)]
    except Exception as e:
        await handle_error(matcher, e)

    if not resp:
        await matcher.finish(Lang.nbp_vrc.user.no_user_found())

    state[KEY_CLIENT] = client
    state[KEY_SEARCH_RESP] = resp

    try:
        pic = await draw_user_card_overview(
            resp,
            group=False,
            client=client,
            title="搜索结果",
        )
    except Exception as e:
        await handle_error(matcher, e)

    msg = Lang.nbp_vrc.user.reply_index()
    if not is_me:
        msg += "\n" + Lang.nbp_vrc.user.reply_index_add()
    await (
        UniMessage.text(Lang.nbp_vrc.user.searched_user_tip(count=len(resp)))
        + UniMessage.image(raw=pic)
        + UniMessage.text(msg)
    ).send()
    end_time = time.perf_counter()
    logger.debug(f"搜索() 执行用时: {end_time - start_time:.3f} 秒")
    await matcher.pause()


@search_user.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    message: Message = EventMessage(),
):
    client: ApiClient = state[KEY_CLIENT]
    resp: List[LimitedUserModel] = state[KEY_SEARCH_RESP]
    arg = message.extract_plain_text().strip()

    # 添加好友
    if arg.startswith("添加"):
        idx_str = arg.replace("添加", "").strip()
        index = await parse_index(idx_str, resp, matcher)
        user_id = resp[index].user_id

        try:
            fq_msg = await get_friend_status(client, user_id)
        except Exception as e:
            await handle_error(matcher, e)

        if fq_msg.is_friend:
            await matcher.finish(Lang.nbp_vrc.friend.exist_friend())
        if fq_msg.incoming_request and not fq_msg.outgoing_request:
            await matcher.finish(Lang.nbp_vrc.friend.incoming_request())
        if fq_msg.outgoing_request and not fq_msg.incoming_request:
            await matcher.finish(Lang.nbp_vrc.friend.outgoing_request())

        try:
            resp_no = await friend(client, user_id)
        except Exception as e:
            if isinstance(e, ApiException) and e.status == 400:
                await matcher.finish(Lang.nbp_vrc.friend.exist_friend())
            await handle_error(matcher, e)
        logger.debug(resp_no)
        await matcher.finish(Lang.nbp_vrc.friend.sucess_request())

    # 查询好友请求状态
    elif arg.startswith("好友"):
        idx_str = arg.replace("好友", "").strip()
        index = await parse_index(idx_str, resp, matcher)
        user_id = resp[index].user_id
        try:
            fq_msg = await get_friend_status(client, user_id)
        except Exception as e:
            await handle_error(matcher, e)

        if fq_msg.is_friend:
            await matcher.send(Lang.nbp_vrc.friend.exist_friend())
        if fq_msg.incoming_request and not fq_msg.outgoing_request:
            await matcher.send(Lang.nbp_vrc.friend.incoming_request())
        if fq_msg.outgoing_request and not fq_msg.incoming_request:
            await matcher.send(Lang.nbp_vrc.friend.outgoing_request())
        logger.info(fq_msg.is_friend)
        return

    # 查询用户详情
    else:
        if len(resp) == 1:
            index = 0
        else:
            if arg == "0":
                await matcher.finish(Lang.nbp_vrc.general.discard_select())
            index = await parse_index(arg, resp, matcher)

        user_id = resp[index].user_id
        try:
            user = await get_user(client, user_id)
            pic = await draw_user_profile_card(user)
        except Exception as e:
            await handle_error(matcher, e)

        await UniMessage.image(raw=pic).finish()
