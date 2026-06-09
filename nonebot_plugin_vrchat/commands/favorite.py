import json
import time
from typing import List

from loguru import logger
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, EventMessage
from nonebot.typing import T_State
from vrchatapi.models import AddFavoriteRequest

from ..i18n import Lang
from ..vrchat import (
    ApiClient,
    FavoriteModel,
    add_favorite,
    clear_favorite_group,
    get_client,
    get_favorite_group,
    get_favorite_groups,
    get_favorite_limits,
    get_favorites,
    get_user_id,
    remove_favorite,
    update_favorite_group,
)
from ..vrchat.utils import format_datetime
from .utils import (
    KEY_ARG,
    KEY_CLIENT,
    KEY_SEARCH_RESP,
    UserSessionId,
    handle_error,
    register_arg_got_handlers,
    rule_enable,
)

favorites_cmd = on_command(
    "vrccoll",
    aliases={"vrc收藏列表", "vrc我的收藏"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    favorites_cmd,
    lambda _: Lang.nbp_vrc.favorite.send_favorite_type_prompt(),
)


@favorites_cmd.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip().lower()
    if arg == "0":
        await matcher.finish("已取消操作")
    start_time = time.perf_counter()
    if arg not in ["avatar", "world"]:
        await matcher.reject(Lang.nbp_vrc.favorite.send_favorite_type_prompt())

    logger.debug(f"正在获取收藏列表：{arg}")
    try:
        client = await get_client(session_id)
        favorites = [x async for x in get_favorites(client, arg, max_size=20)]
        logger.debug(f"[get_favorites] type={arg}, count={len(favorites)}")
        if favorites:
            logger.debug(f"[get_favorites] 第一条：{favorites[0]}")
    except Exception as e:
        await handle_error(matcher, e)
        return
    logger.debug(f"收藏列表，共 {len(favorites)} 个")
    if not favorites:
        await matcher.finish(Lang.nbp_vrc.favorite.empty_favorite_list(type=arg))

    state[KEY_CLIENT] = client
    state[KEY_SEARCH_RESP] = favorites
    state["favorite_type"] = arg

    end_time = time.perf_counter()
    logger.debug(f"收藏列表获取执行用时：{end_time - start_time:.3f} 秒")

    msg = f"收藏列表 ({arg})，共 {len(favorites)} 个：\n\n"
    for i, fav in enumerate(favorites[:20], 1):
        msg += f"{i}. ID: {fav.favorite_id_ref}\n"
        msg += f"   收藏组：{fav.group}\n"
        msg += f"   标签：{', '.join(fav.tags)}\n"
        msg += f"   更新时间：{format_datetime(fav.updated_at)}\n\n"

    msg += "发送序号查看详情，或发送【删除 1】删除第 1 个收藏，发送 0 取消"
    await matcher.send(msg)
    await matcher.pause()


@favorites_cmd.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    message: Message = EventMessage(),
):
    client: ApiClient = state[KEY_CLIENT]
    favorites: List[FavoriteModel] = state[KEY_SEARCH_RESP]
    # favorite_type = state["favorite_type"]
    arg = message.extract_plain_text().strip()

    if arg == "0":
        await matcher.finish("已取消操作")

    if arg.startswith("删除"):
        idx_str = arg.replace("删除", "").strip()
        if not idx_str.isdigit():
            await matcher.reject("序号格式不正确")
        index = int(idx_str) - 1
        if index < 0 or index >= len(favorites):
            await matcher.reject("序号不在范围内")

        favorite_id = favorites[index].favorite_id
        logger.info(f"正在删除收藏：{favorite_id}")
        try:
            result = await remove_favorite(client, favorite_id)
        except Exception as e:
            await handle_error(matcher, e)
            return
        if result:
            await matcher.finish("已成功删除收藏")
        else:
            await matcher.finish("删除收藏失败")

    else:
        if len(favorites) == 1:
            index = 0
        else:
            if arg == "0":
                await matcher.finish("已取消操作")
            if not arg.isdigit():
                await matcher.reject("序号格式不正确")
            index = int(arg) - 1
            if index < 0 or index >= len(favorites):
                await matcher.reject("序号不在范围内")

        fav = favorites[index]
        msg = "收藏详情：\n\n"
        msg += f"收藏 ID: {fav.favorite_id}\n"
        msg += f"引用 ID: {fav.id}\n"
        msg += f"类型：{fav.type}\n"

        if fav.tags:
            msg += f"标签：{', '.join(fav.tags)}\n"
        await matcher.finish(msg)


favorite_groups_cmd = on_command(
    "vrcfgl",
    aliases={"vrc收藏组列表", "vrc我的收藏组"},
    rule=rule_enable,
    priority=20,
)


@favorite_groups_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
):
    logger.info("正在获取收藏组列表")
    try:
        client = await get_client(session_id)
        groups = [x async for x in get_favorite_groups(client, max_size=50)]
        logger.debug(f"[get_favorite_groups] count={len(groups)}")
        if groups:
            logger.debug(f"[get_favorite_groups] 第一条：{groups[0]}")
    except Exception as e:
        await handle_error(matcher, e)
        return
    if not groups:
        await matcher.finish("没有收藏组")

    avatar_groups = [g for g in groups if g.type == "avatar"]
    world_groups = [g for g in groups if g.type == "world"]
    friend_groups = [g for g in groups if g.type == "friend"]

    msg = f"收藏组列表，共 {len(groups)} 个：\n\n"

    msg += f"【Avatar】{len(avatar_groups)} 个\n"
    for i, group in enumerate(avatar_groups[:10], 1):
        msg += f"  {i}. {group.display_name} ({group.name})\n"
        msg += f"     所有者：{group.owner_id}\n"
        msg += f"     可见性：{group.visibility}\n"
        if group.tags:
            msg += f"     标签：{', '.join(group.tags)}\n"
    if len(avatar_groups) > 10:
        msg += f"  ... 还有 {len(avatar_groups) - 10} 个\n"
    msg += "\n"

    msg += f"【World】{len(world_groups)} 个\n"
    for i, group in enumerate(world_groups[:10], 1):
        msg += f"  {i}. {group.display_name} ({group.name})\n"
        msg += f"     所有者：{group.owner_id}\n"
        msg += f"     可见性：{group.visibility}\n"
        if group.tags:
            msg += f"     标签：{', '.join(group.tags)}\n"
    if len(world_groups) > 10:
        msg += f"  ... 还有 {len(world_groups) - 10} 个\n"
    msg += "\n"

    msg += f"【Friend】{len(friend_groups)} 个\n"
    for i, group in enumerate(friend_groups[:10], 1):
        msg += f"  {i}. {group.display_name} ({group.name})\n"
        msg += f"     所有者：{group.owner_id}\n"
        msg += f"     可见性：{group.visibility}\n"
        if group.tags:
            msg += f"     标签：{', '.join(group.tags)}\n"
    if len(friend_groups) > 10:
        msg += f"  ... 还有 {len(friend_groups) - 10} 个\n"

    await matcher.finish(msg)


favorite_limits_cmd = on_command(
    "vrcflim",
    aliases={"vrc收藏限制", "vrc收藏容量"},
    rule=rule_enable,
    priority=20,
)


@favorite_limits_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
):
    logger.info("正在获取收藏限制信息")
    try:
        client = await get_client(session_id)
        limits = await get_favorite_limits(client)
        logger.debug(f"[get_favorite_limits] {limits.model_dump()}")
    except Exception as e:
        await handle_error(matcher, e)
        return
    msg = "最大收藏限制信息：\n\n"
    msg += f"[群组] 数：{limits.default_max_favorite_groups}\n"
    msg += f"[群组][项] 数：{limits.default_max_favorites_per_group}\n"

    msg += f"[模型组] 数：{limits.max_favorite_groups.avatar + limits.max_favorite_groups.friend + limits.max_favorite_groups.vrc_plus_world + limits.max_favorite_groups.world}\n"
    msg += f"[模型组][项] 数：{limits.max_favorites_per_group.avatar + limits.max_favorites_per_group.friend + limits.max_favorites_per_group.vrc_plus_world + limits.max_favorites_per_group.world}\n"

    await matcher.finish(msg)


add_favorite_cmd = on_command(
    "vrcfav",
    aliases={"vrc添加收藏", "vrc加入收藏"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    add_favorite_cmd,
    lambda _: (
        Lang.nbp_vrc.favorite.send_add_favorite_info_v2()
        + "\n"
        + Lang.nbp_vrc.favorite.add_favorite_example()
    ),
)


@add_favorite_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject(
            Lang.nbp_vrc.favorite.send_add_favorite_info_v2()
            + "\n"
            + Lang.nbp_vrc.favorite.add_favorite_example(),
        )

    parts = arg.split()
    if len(parts) < 2:
        await matcher.reject("格式错误，请发送 [类型] [引用 ID] [标签]")

    favorite_type = parts[0].lower()
    favorite_id_ref = parts[1]

    tags_list = [] if len(parts) < 3 else parts[2:]

    if favorite_type not in ["avatar", "world", "friend"]:
        await matcher.reject(Lang.nbp_vrc.favorite.invalid_favorite_type_v2())

    logger.info(f"正在添加收藏：{favorite_type} - {favorite_id_ref}")
    try:
        client = await get_client(session_id)
        add_favorite_request = AddFavoriteRequest(
            type=favorite_type.lower(),
            favorite_id=favorite_id_ref,
            tags=tags_list,
        )
        result = await add_favorite(client, add_favorite_request)
    except Exception as e:
        await handle_error(matcher, e)
        return

    if result:
        await matcher.finish(
            Lang.nbp_vrc.favorite.success_add(favorite_id=favorite_id_ref),
        )
    else:
        await matcher.finish(Lang.nbp_vrc.favorite.error_handle())


remove_favorite_cmd = on_command(
    "vrcfdel",
    aliases={"vrc删除收藏", "vrc移除收藏"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    remove_favorite_cmd,
    lambda _: Lang.nbp_vrc.favorite.send_favorite_id(),
)


@remove_favorite_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject(Lang.nbp_vrc.favorite.send_favorite_id())

    logger.info(f"正在删除收藏：{arg}")
    try:
        client = await get_client(session_id)
        result = await remove_favorite(client, arg)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish(Lang.nbp_vrc.favorite.success_remove())
    else:
        await matcher.finish(Lang.nbp_vrc.favorite.error_handle())


update_favorite_group_cmd = on_command(
    "vrcfug",
    aliases={"vrc更新收藏组"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    update_favorite_group_cmd,
    lambda _: (
        "请发送收藏组类型 收藏组名称 和 更新数据 (JSON)，或发送【类型 名称 用户 ID JSON】指定用户"
    ),
)


@update_favorite_group_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject(
            "请发送收藏组类型 收藏组名称 和 更新数据 (JSON)，或发送【类型 名称 用户 ID JSON】指定用户",
        )

    saved_user_id = get_user_id(session_id)

    parts = arg.split(maxsplit=3)
    if len(parts) == 3:
        favorite_group_type, favorite_group_name, update_data = parts
        user_id = saved_user_id
        if not user_id:
            await matcher.reject(
                "未找到已保存的用户 ID，请发送【类型 名称 用户 ID JSON】",
            )
    elif len(parts) == 4:
        favorite_group_type, favorite_group_name, user_id, update_data = parts
    else:
        await matcher.reject("格式错误，请发送 收藏组类型 收藏组名称 [用户 ID] JSON")

    logger.info(f"正在更新收藏组：{favorite_group_type} - {favorite_group_name}")
    try:
        client = await get_client(session_id)
        update_request = json.loads(update_data)
        result = await update_favorite_group(
            client,
            favorite_group_type,
            favorite_group_name,
            user_id,
            update_request,
        )
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish(f"已成功更新收藏组：{favorite_group_name}")
    else:
        await matcher.finish("更新收藏组失败")


clear_favorite_group_cmd = on_command(
    "vrcfcg",
    aliases={"vrc清空收藏组"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    clear_favorite_group_cmd,
    lambda _: "请发送收藏组类型 收藏组名称，或发送【类型 名称 用户 ID】指定用户",
)


@clear_favorite_group_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject(
            "请发送收藏组类型 收藏组名称，或发送【类型 名称 用户 ID】指定用户",
        )

    saved_user_id = get_user_id(session_id)

    parts = arg.split()
    if len(parts) == 2:
        favorite_group_type, favorite_group_name = parts
        user_id = saved_user_id
        if not user_id:
            await matcher.reject("未找到已保存的用户 ID，请发送【类型 名称 用户 ID】")
    elif len(parts) == 3:
        favorite_group_type, favorite_group_name, user_id = parts
    else:
        await matcher.reject("格式错误，请发送 收藏组类型 收藏组名称 [用户 ID]")

    logger.info(f"正在清空收藏组：{favorite_group_type} - {favorite_group_name}")
    try:
        client = await get_client(session_id)
        result = await clear_favorite_group(
            client,
            favorite_group_type,
            favorite_group_name,
            user_id,
        )
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish(f"已成功清空收藏组：{favorite_group_name}")
    else:
        await matcher.finish("清空收藏组失败")


get_favorite_group_cmd = on_command(
    "vrcfg",
    aliases={"vrc获取收藏组", "vrc收藏组详情"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    get_favorite_group_cmd,
    lambda _: "请发送收藏组类型 收藏组名称，或发送【类型 名称 用户 ID】指定用户",
)


@get_favorite_group_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject(
            "请发送收藏组类型 收藏组名称，或发送【类型 名称 用户 ID】指定用户",
        )

    parts = arg.split()

    saved_user_id = get_user_id(session_id)

    if len(parts) == 2:
        favorite_group_type, favorite_group_name = parts
        user_id = saved_user_id
        if not user_id:
            await matcher.reject("未找到已保存的用户 ID，请发送【类型 名称 用户 ID】")
    elif len(parts) == 3:
        favorite_group_type, favorite_group_name, user_id = parts
    else:
        await matcher.reject("格式错误，请发送 收藏组类型 收藏组名称 [用户 ID]")

    logger.info(f"正在获取收藏组：{favorite_group_type} - {favorite_group_name}")
    try:
        client = await get_client(session_id)
        group = await get_favorite_group(
            client,
            favorite_group_type,
            favorite_group_name,
            user_id,
        )
        logger.debug(f"[get_favorite_group] {group}")
    except Exception as e:
        await handle_error(matcher, e)
        return
    msg = "收藏组详情：\n\n"
    msg += f"名称：{group.display_name} ({group.name})\n"
    msg += f"类型：{group.type}\n"
    msg += f"所有者：{group.owner_display_name}\n"
    msg += f"可见性：{group.visibility}\n"
    if group.tags:
        msg += f"标签：{', '.join(group.tags)}\n"

    await matcher.finish(msg)


favorite_help = on_command(
    "vrcfavoritehelp",
    aliases={"vrc收藏帮助"},
    rule=rule_enable,
    priority=20,
)


@favorite_help.handle()
async def _(matcher: Matcher):
    msg = """--------vrc收藏指令--------
【查询】
1、【vrc收藏列表】【avatar/world/friend】| 查看收藏列表 (未完成)
2、【vrc收藏组列表】| 查看收藏组列表
3、【vrc收藏限制】| 查看收藏容量限制
4、【vrc收藏组详情】【类型 名称 用户 ID】| 查看收藏组详情

【操作】
5、【vrc添加收藏】【类型 引用 ID】| 添加收藏
6、【vrc删除收藏】【收藏 ID】| 删除收藏
7、【vrc更新收藏组】【类型 名称 用户 ID JSON】| 更新收藏组
8、【vrc清空收藏组】【类型 名称 用户 ID】| 清空收藏组"""
    await matcher.finish(msg)
