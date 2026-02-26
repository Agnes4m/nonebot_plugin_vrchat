import time
from datetime import datetime
from typing import List

from loguru import logger
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, EventMessage
from nonebot.typing import T_State

from ..vrchat import (
    ApiClient,
    LimitedGroupModel,
    get_client,
    get_group,
    get_group_announcements,
    get_group_instances,
    get_group_members,
    get_group_requests,
    get_group_roles,
    join_group,
    leave_group,
    search_groups,
)
from .utils import (
    KEY_ARG,
    KEY_CLIENT,
    KEY_SEARCH_RESP,
    UserSessionId,
    handle_error,
    parse_group_index,
    register_arg_got_handlers,
    rule_enable,
)


def format_datetime(dt: datetime | str | None) -> str:
    """格式化 datetime 对象为易读字符串"""
    if not dt:
        return "未知"
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)


# region 搜索群组
search_group = on_command(
    "vrcsg",
    aliases={"vrc搜索群组", "vrc群组搜索"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    search_group,
    lambda matcher: "请发送要搜索的群组名称",  # noqa: ARG005
)


@search_group.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    start_time = time.perf_counter()
    if not arg:
        await matcher.reject("请发送要搜索的群组名称")

    logger.info(f"正在搜索群组：{arg}")
    try:
        client = await get_client(session_id)
        groups = [x async for x in search_groups(client, arg, max_size=10)]
    except Exception as e:
        await handle_error(matcher, e)

    if not groups:
        await matcher.finish("未找到相关群组")

    state[KEY_CLIENT] = client
    state[KEY_SEARCH_RESP] = groups

    end_time = time.perf_counter()
    logger.debug(f"群组搜索执行用时：{end_time - start_time:.3f} 秒")

    msg = f"搜索到 {len(groups)} 个群组：\n\n"
    for i, group in enumerate(groups[:10], 1):
        msg += f"{i}. {group.name}\n"
        msg += f"   ID: {group.group_id}\n"
        msg += f"   成员数：{group.member_count}\n"
        msg += f"   描述：{group.description[:50]}...\n\n"

    msg += "发送序号查看详情，或发送【加入 1】加入第 1 个群组，发送 0 取消"
    await matcher.send(msg)
    await matcher.pause()


@search_group.handle()
async def _(
    matcher: Matcher,
    state: T_State,
    message: Message = EventMessage(),
):
    client: ApiClient = state[KEY_CLIENT]
    groups: List[LimitedGroupModel] = state[KEY_SEARCH_RESP]
    arg = message.extract_plain_text().strip()

    # 取消操作
    if arg == "0":
        await matcher.finish("已取消操作")

    # 加入群组
    if arg.startswith("加入"):
        idx_str = arg.replace("加入", "").strip()
        index = await parse_group_index(idx_str, groups, matcher)
        group_id = groups[index].group_id

        logger.info(f"正在申请加入群组：{group_id}")
        try:
            result = await join_group(client, group_id)
        except Exception as e:
            await handle_error(matcher, e)

        if result:
            await matcher.finish("已成功申请加入群组")
        else:
            await matcher.finish("加入群组失败")

    # 查看详情
    else:
        if len(groups) == 1:
            index = 0
        else:
            if arg == "0":
                await matcher.finish("已取消操作")
            index = await parse_group_index(arg, groups, matcher)

        group = groups[index]
        try:
            group_detail = await get_group(client, group.group_id)
        except Exception as e:
            await handle_error(matcher, e)
            return

        msg = "群组信息：\n\n"
        msg += f"名称：{group_detail.name}\n"
        msg += f"ID: {group_detail.group_id}\n"
        msg += f"短代码：{group_detail.short_code}#{group_detail.discriminator}\n"
        msg += f"成员数：{group_detail.member_count}\n"
        msg += f"在线成员：{group_detail.online_member_count}\n"
        msg += f"描述：{group_detail.description}\n"
        msg += f"隐私：{group_detail.privacy}\n"
        msg += f"加入状态：{group_detail.join_state}\n"
        msg += f"语言：{', '.join(group_detail.languages)}\n"

        await matcher.finish(msg)


# region 群组详情
group_info = on_command(
    "vrcgi",
    aliases={"vrc群组信息", "vrc群组详情"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    group_info,
    lambda matcher: "请发送群组 ID 或群组名称",  # noqa: ARG005
)


@group_info.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID 或群组名称")

    logger.info(f"正在查询群组：{arg}")
    try:
        client = await get_client(session_id)
        # 尝试直接使用 arg 作为 group_id
        group = await get_group(client, arg)
    except Exception:
        # 如果不是有效的 group_id，尝试搜索
        try:
            client = await get_client(session_id)
            groups = [x async for x in search_groups(client, arg, max_size=1)]
            if not groups:
                await matcher.finish("未找到相关群组")
            group = groups[0]
        except Exception as e:
            await handle_error(matcher, e)
            return

    msg = "群组信息：\n\n"
    msg += f"名称：{group.name}\n"
    msg += f"ID: {group.group_id}\n"
    msg += f"短代码：{group.short_code}#{group.discriminator}\n"
    msg += f"成员数：{group.member_count}\n"
    msg += f"描述：{group.description}\n"
    if group.icon_url:
        msg += f"图标：{group.icon_url}\n"
    if group.banner_url:
        msg += f"横幅：{group.banner_url}\n"
    if group.owner_id:
        msg += f"所有者：{group.owner_id}\n"
    if group.membership_status:
        msg += f"成员状态：{group.membership_status}\n"

    await matcher.finish(msg)


# region 群组成员
group_members_cmd = on_command(
    "vrcgm",
    aliases={"vrc群组成员", "vrc群组成员列表"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    group_members_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@group_members_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在获取群组成员：{arg}")
    try:
        client = await get_client(session_id)
        members = await get_group_members(client, arg, n=20)
    except Exception as e:
        await handle_error(matcher, e)

    if not members:
        await matcher.finish("该群组没有成员或获取失败")
    msg = f"群组成员列表 (共 {len(members)} 人)：\n\n"
    for i, member in enumerate(members[:20], 1):
        data = member.get("user", {})
        user_id = data.get("user_id", "未知")
        display_name = data.get("display_name", "未知")
        # current_avatar_thumbnail_image_url = data.current_avatar_thumbnail_image_url # 头像
        # profile_pic_override = data.profile_pic_override # 部分有
        # thumbnail_url = data.thumbnail_url # 首页图

        msg += f"{i}. 昵称：{display_name}\n"
        msg += f"   用户 ID: {user_id}\n"
        msg += f"   加入时间：{format_datetime(member.get('joined_at'))}\n"
        msg += f"   成员状态：{member.get('membership_status', '未知')}\n"
        if member.get("is_representing"):
            msg += "   正在代表群组\n"
        msg += "\n"

    await matcher.finish(msg)


# region 群组角色
group_roles_cmd = on_command(
    "vrcgr",
    aliases={"vrc群组角色", "vrc群组职位"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    group_roles_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@group_roles_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在获取群组角色：{arg}")
    try:
        client = await get_client(session_id)
        roles = await get_group_roles(client, arg)
    except Exception as e:
        await handle_error(matcher, e)

    if not roles:
        await matcher.finish("该群组没有角色或获取失败")
    msg = f"群组角色列表 (共 {len(roles)} 个)：\n\n"
    for i, role in enumerate(roles[:20], 1):
        msg += f"{i}. {role.get('name', '未知')}\n"
        msg += f"   ID: {role.get('id', '未知')}\n"
        msg += f"   描述：{role.get('description', '无')}\n"
        msg += f"   权限：{role.get('permissions', [])}\n"
        msg += f"   创建时间：{format_datetime(role.get('created_at'))}\n"
        update_at = format_datetime(role.get("updated_at"))
        msg += f"   更新时间：{update_at}\n" if update_at else ""
        tag = "关键词: "
        if role.get("is_self_assignable"):
            tag += "   可自由加入"
        if role.get("is_management_role"):
            tag += "   管理角色"
        if role.get("requires_two_factor"):
            tag += "   需要二步验证"
        if role.get("requires_purchase"):
            tag += "   需要购买"
        msg += tag + "\n" if tag else ""

    await matcher.finish(msg)


# region 群组公告
group_announcements_cmd = on_command(
    "vrcga",
    aliases={"vrc群组公告"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    group_announcements_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@group_announcements_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在获取群组公告：{arg}")
    try:
        client = await get_client(session_id)
        announcements = await get_group_announcements(client, arg)
    except Exception as e:
        await handle_error(matcher, e)

    if not announcements:
        await matcher.finish("该群组没有公告")

    msg = "群组公告：\n\n"
    msg += f"标题：{announcements.get('title', '无标题')}\n"
    msg += f"作者：{announcements.get('author_id', '未知')}\n"
    msg += f"内容：{announcements.get('text', '')[:200]}...\n"
    if announcements.get("image_url"):
        msg += f"图片：{announcements.get('image_url')}\n"
    msg += f"更新时间：{format_datetime(announcements.get('updated_at'))}\n"

    await matcher.finish(msg)


# region 加入群组
join_group_cmd = on_command(
    "vrcjg",
    aliases={"vrc加入群组", "vrc申请群组"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    join_group_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@join_group_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在申请加入群组：{arg}")
    try:
        client = await get_client(session_id)
        result = await join_group(client, arg)
    except Exception as e:
        await handle_error(matcher, e)

    if result:
        await matcher.finish("已成功申请加入群组")
    else:
        await matcher.finish("加入群组失败")


# region 离开群组
leave_group_cmd = on_command(
    "vrclg",
    aliases={"vrc离开群组", "vrc退出群组"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    leave_group_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@leave_group_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在离开群组：{arg}")
    try:
        client = await get_client(session_id)
        result = await leave_group(client, arg)
    except Exception as e:
        await handle_error(matcher, e)

    if result:
        await matcher.finish("已成功离开群组")
    else:
        await matcher.finish("离开群组失败")


# region 群组请求
group_requests_cmd = on_command(
    "vrcgreq",
    aliases={"vrc群组请求", "vrc入群申请"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    group_requests_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@group_requests_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在获取群组请求：{arg}")
    try:
        client = await get_client(session_id)
        requests = await get_group_requests(client, arg, n=20)
    except Exception as e:
        await handle_error(matcher, e)

    if not requests:
        await matcher.finish("该群组没有待处理的请求")

    msg = f"群组请求列表 (共 {len(requests)} 个)：\n\n"
    for i, req in enumerate(requests[:20], 1):
        msg += f"{i}. 用户 ID: {req.get('user_id', '未知')}\n"
        msg += f"   请求时间：{format_datetime(req.get('created_at'))}\n"
        msg += f"   成员状态：{req.get('membership_status', '未知')}\n"
        if req.get("has_joined_from_purchase"):
            msg += "   通过购买加入\n"
        msg += "\n"


# region 群组实例
group_instances_cmd = on_command(
    "vrcgi2",
    aliases={"vrc群组实例", "vrc群组房间"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    group_instances_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@group_instances_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在获取群组实例：{arg}")
    try:
        client = await get_client(session_id)
        instances = await get_group_instances(client, arg)
    except Exception as e:
        await handle_error(matcher, e)

    if not instances:
        await matcher.finish("该群组当前没有活跃的实例")

    msg = f"群组实例列表 (共 {len(instances)} 个)：\n\n"
    for i, inst in enumerate(instances[:20], 1):
        msg += f"{i}. 实例 ID: {inst.get('instance_id', '未知')}\n"
        msg += f"   位置：{inst.get('location', '未知')}\n"
        msg += f"   成员数：{inst.get('member_count', 0)}\n"
        world = inst.get("world", {})
        if isinstance(world, dict):
            msg += f"   世界名称：{world.get('name', '未知')}\n"
        msg += "\n"


# region 群组帮助
group_help = on_command(
    "vrcgrouphelp",
    aliases={"vrc群组帮助"},
    rule=rule_enable,
    priority=20,
)


@group_help.handle()
async def _(matcher: Matcher):
    msg = """--------vrc 群组指令--------
1、【vrc搜索群组】【关键词】| 搜索群组
2、【vrc群组信息】【群组 ID/名称】| 查看群组详情
3、【vrc群组成员】【群组 ID】| 查看成员列表
4、【vrc群组角色】【群组 ID】| 查看角色列表
5、【vrc群组公告】【群组 ID】| 查看公告列表
6、【vrc加入群组】【群组 ID】| 申请加入群组
7、【vrc离开群组】【群组 ID】| 离开群组
8、【vrc群组请求】【群组 ID】| 查看入群申请
9、【vrc群组实例】【群组 ID】| 查看群组实例"""
    await matcher.finish(msg)
