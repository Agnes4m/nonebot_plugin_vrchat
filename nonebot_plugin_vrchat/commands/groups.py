import time
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
    add_member_role,
    ban_group_member,
    cancel_group_join_request,
    # 公告管理
    create_group_announcement,
    # 帖子管理
    create_group_post,
    delete_group_announcement,
    delete_group_invite,
    delete_group_post,
    get_client,
    get_group,
    get_group_announcements,
    # 审计日志
    get_group_audit_logs,
    # 封禁管理
    get_group_bans,
    # 画廊管理
    get_group_gallery,
    get_group_gallery_images,
    get_group_instances,
    get_group_invites,
    get_group_members,
    # 权限
    get_group_permissions,
    get_group_posts,
    get_group_requests,
    get_group_roles,
    get_my_group_member,
    # 邀请管理
    invite_user_to_group,
    join_group,
    # 成员管理
    kick_group_member,
    leave_group,
    remove_member_role,
    # 请求管理
    respond_to_group_join_request,
    search_groups,
    unban_group_member,
    # 代表身份
    update_group_representation,
)
from ..vrchat.utils import format_datetime
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
        return
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
            return
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
        return
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
        return
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
        return
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
        return
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
        return
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
        return

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
    await matcher.finish(msg)


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
        return

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
    await matcher.finish(msg)


# region 群组权限
group_permissions_cmd = on_command(
    "vrcgp",
    aliases={"vrc群组权限"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    group_permissions_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@group_permissions_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在获取群组权限：{arg}")
    try:
        client = await get_client(session_id)
        permissions = await get_group_permissions(client, arg)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if not permissions:
        await matcher.finish("无法获取群组权限")

    msg = "群组权限信息：\n\n"
    for key, value in permissions.items():
        msg += f"{key}: {value}\n"
    await matcher.finish(msg)


# region 我的群组成员信息
my_group_member_cmd = on_command(
    "vrcmgm",
    aliases={"vrc我的群组信息", "vrc我加入的群组"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    my_group_member_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@my_group_member_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在获取我的群组成员信息：{arg}")
    try:
        client = await get_client(session_id)
        member_info = await get_my_group_member(client, arg)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if not member_info:
        await matcher.finish("无法获取我的群组成员信息")

    msg = "我的群组成员信息：\n\n"
    msg += f"用户 ID: {member_info.get('user', {}).get('id', '未知')}\n"
    msg += f"成员状态：{member_info.get('membership_status', '未知')}\n"
    msg += f"加入时间：{format_datetime(member_info.get('created_at'))}\n"
    msg += f"更新时间：{format_datetime(member_info.get('updated_at'))}\n"
    if member_info.get("is_representing"):
        msg += "正在代表群组\n"
    roles = member_info.get("roles", [])
    if roles:
        msg += f"角色列表：{', '.join([r.get('name', '未知') for r in roles])}\n"
    await matcher.finish(msg)


# region 更新群组代表身份
update_group_rep_cmd = on_command(
    "vrcugr",
    aliases={"vrc更新群组代表", "vrc代表群组"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    update_group_rep_cmd,
    lambda matcher: "请发送群组 ID，或发送 取消 代表群组",  # noqa: ARG005
)


@update_group_rep_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID，或发送 取消 代表群组")

    logger.info(f"正在更新群组代表身份：{arg}")
    try:
        client = await get_client(session_id)
        represent = arg.lower() not in ["取消", "false", "0", "no"]
        result = await update_group_representation(client, arg, represent)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        status = "代表群组" if represent else "取消代表群组"
        await matcher.finish(f"已{status}")
    else:
        await matcher.finish("更新群组代表身份失败")


# region 踢出群组成员
kick_member_cmd = on_command(
    "vrcgmk",
    aliases={"vrc踢出成员", "vrc踢出群组成员"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    kick_member_cmd,
    lambda matcher: "请发送群组 ID 和 用户 ID，用空格分隔",  # noqa: ARG005
)


@kick_member_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID 和 用户 ID，用空格分隔")

    parts = arg.split()
    if len(parts) != 2:
        await matcher.reject("格式错误，请发送 群组 ID 用户 ID")

    group_id, user_id = parts
    logger.info(f"正在踢出群组成员：{group_id} - {user_id}")
    try:
        client = await get_client(session_id)
        result = await kick_group_member(client, group_id, user_id)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish(f"已将用户 {user_id} 踢出群组")
    else:
        await matcher.finish("踢出成员失败")


# region 添加成员角色
add_role_cmd = on_command(
    "vrcgmr",
    aliases={"vrc添加成员角色", "vrc给予职位"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    add_role_cmd,
    lambda matcher: "请发送群组 ID 用户 ID 角色 ID，用空格分隔",  # noqa: ARG005
)


@add_role_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID 用户 ID 角色 ID，用空格分隔")

    parts = arg.split()
    if len(parts) != 3:
        await matcher.reject("格式错误，请发送 群组 ID 用户 ID 角色 ID")

    group_id, user_id, role_id = parts
    logger.info(f"正在添加成员角色：{group_id} - {user_id} - {role_id}")
    try:
        client = await get_client(session_id)
        result = await add_member_role(client, group_id, user_id, role_id)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish(f"已给用户 {user_id} 添加角色 {role_id}")
    else:
        await matcher.finish("添加角色失败")


# region 移除成员角色
remove_role_cmd = on_command(
    "vrcgmr2",
    aliases={"vrc移除成员角色", "vrc撤销职位"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    remove_role_cmd,
    lambda matcher: "请发送群组 ID 用户 ID 角色 ID，用空格分隔",  # noqa: ARG005
)


@remove_role_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID 用户 ID 角色 ID，用空格分隔")

    parts = arg.split()
    if len(parts) != 3:
        await matcher.reject("格式错误，请发送 群组 ID 用户 ID 角色 ID")

    group_id, user_id, role_id = parts
    logger.info(f"正在移除成员角色：{group_id} - {user_id} - {role_id}")
    try:
        client = await get_client(session_id)
        result = await remove_member_role(client, group_id, user_id, role_id)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish(f"已移除用户 {user_id} 的角色 {role_id}")
    else:
        await matcher.finish("移除角色失败")


# region 创建群组公告
create_announcement_cmd = on_command(
    "vrcgca",
    aliases={"vrc创建公告"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    create_announcement_cmd,
    lambda matcher: "请发送群组 ID 和公告标题，用空格分隔",  # noqa: ARG005
)


@create_announcement_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID 和公告标题，用空格分隔")

    parts = arg.split(maxsplit=2)
    if len(parts) < 2:
        await matcher.reject("格式错误，请发送 群组 ID 标题 内容")

    group_id = parts[0]
    title = parts[1]
    text = parts[2] if len(parts) > 2 else ""

    logger.info(f"正在创建群组公告：{group_id} - {title}")
    try:
        client = await get_client(session_id)
        result = await create_group_announcement(client, group_id, title, text)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish(f"公告创建成功：{title}")
    else:
        await matcher.finish("创建公告失败")


# region 删除群组公告
delete_announcement_cmd = on_command(
    "vrcgda",
    aliases={"vrc删除公告"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    delete_announcement_cmd,
    lambda matcher: "请发送群组 ID 和公告 ID，用空格分隔",  # noqa: ARG005
)


@delete_announcement_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID 和公告 ID，用空格分隔")

    parts = arg.split()
    if len(parts) != 2:
        await matcher.reject("格式错误，请发送 群组 ID 公告 ID")

    group_id, announcement_id = parts
    logger.info(f"正在删除群组公告：{group_id} - {announcement_id}")
    try:
        client = await get_client(session_id)
        result = await delete_group_announcement(client, group_id, announcement_id)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish("公告已删除")
    else:
        await matcher.finish("删除公告失败")


# region 创建群组帖子
create_post_cmd = on_command(
    "vrcgcp",
    aliases={"vrc创建帖子"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    create_post_cmd,
    lambda matcher: "请发送群组 ID 和帖子标题，用空格分隔",  # noqa: ARG005
)


@create_post_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID 和帖子标题，用空格分隔")

    parts = arg.split(maxsplit=2)
    if len(parts) < 2:
        await matcher.reject("格式错误，请发送 群组 ID 标题 内容")

    group_id = parts[0]
    title = parts[1]
    text = parts[2] if len(parts) > 2 else ""

    logger.info(f"正在创建群组帖子：{group_id} - {title}")
    try:
        client = await get_client(session_id)
        result = await create_group_post(client, group_id, title, text)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish(f"帖子创建成功：{title}")
    else:
        await matcher.finish("创建帖子失败")


# region 群组帖子列表
group_posts_cmd = on_command(
    "vrcgpl",
    aliases={"vrc帖子列表"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    group_posts_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@group_posts_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在获取群组帖子：{arg}")
    try:
        client = await get_client(session_id)
        posts = await get_group_posts(client, arg, n=20)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if not posts:
        await matcher.finish("该群组没有帖子")

    msg = f"群组帖子列表 (共 {len(posts)} 个)：\n\n"
    for i, post in enumerate(posts[:20], 1):
        msg += f"{i}. {post.get('title', '无标题')}\n"
        msg += f"   作者：{post.get('author', {}).get('display_name', '未知')}\n"
        msg += f"   创建时间：{format_datetime(post.get('created_at'))}\n"
        msg += f"   内容：{post.get('text', '')[:50]}...\n\n"

    await matcher.finish(msg)


# region 删除群组帖子
delete_post_cmd = on_command(
    "vrcgdp",
    aliases={"vrc删除帖子"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    delete_post_cmd,
    lambda matcher: "请发送群组 ID 和帖子 ID，用空格分隔",  # noqa: ARG005
)


@delete_post_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID 和帖子 ID，用空格分隔")

    parts = arg.split()
    if len(parts) != 2:
        await matcher.reject("格式错误，请发送 群组 ID 帖子 ID")

    group_id, post_id = parts
    logger.info(f"正在删除群组帖子：{group_id} - {post_id}")
    try:
        client = await get_client(session_id)
        result = await delete_group_post(client, group_id, post_id)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish("帖子已删除")
    else:
        await matcher.finish("删除帖子失败")


# region 群组画廊
group_gallery_cmd = on_command(
    "vrcgg",
    aliases={"vrc群组画廊"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    group_gallery_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@group_gallery_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在获取群组画廊：{arg}")
    try:
        client = await get_client(session_id)
        gallery = await get_group_gallery(client, arg)
        images = await get_group_gallery_images(client, arg, n=20)
    except Exception as e:
        await handle_error(matcher, e)
        return
    msg = "群组画廊信息：\n\n"
    msg += f"画廊 ID: {gallery.get('id', '未知')}\n"
    msg += f"图片数量：{len(images)}\n\n"

    if images:
        msg += "图片列表：\n"
        for i, img in enumerate(images[:20], 1):
            msg += f"{i}. {img.get('file_id', '未知')}\n"
            msg += f"   描述：{img.get('description', '无')}\n"
            msg += f"   创建时间：{format_datetime(img.get('created_at'))}\n\n"

    await matcher.finish(msg)


# region 邀请用户到群组
invite_user_cmd = on_command(
    "vrcgui",
    aliases={"vrc邀请用户", "vrc邀请入群"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    invite_user_cmd,
    lambda matcher: "请发送群组 ID 和 用户 ID，用空格分隔",  # noqa: ARG005
)


@invite_user_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID 和 用户 ID，用空格分隔")

    parts = arg.split()
    if len(parts) != 2:
        await matcher.reject("格式错误，请发送 群组 ID 用户 ID")

    group_id, user_id = parts
    logger.info(f"正在邀请用户：{group_id} - {user_id}")
    try:
        client = await get_client(session_id)
        result = await invite_user_to_group(client, group_id, user_id)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish(f"已邀请用户 {user_id} 加入群组")
    else:
        await matcher.finish("邀请用户失败")


# region 删除群组邀请
delete_invite_cmd = on_command(
    "vrcgdi",
    aliases={"vrc删除邀请"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    delete_invite_cmd,
    lambda matcher: "请发送群组 ID 和 用户 ID，用空格分隔",  # noqa: ARG005
)


@delete_invite_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID 和 用户 ID，用空格分隔")

    parts = arg.split()
    if len(parts) != 2:
        await matcher.reject("格式错误，请发送 群组 ID 用户 ID")

    group_id, user_id = parts
    logger.info(f"正在删除群组邀请：{group_id} - {user_id}")
    try:
        client = await get_client(session_id)
        result = await delete_group_invite(client, group_id, user_id)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish(f"已删除用户 {user_id} 的群组邀请")
    else:
        await matcher.finish("删除邀请失败")


# region 群组邀请列表
group_invites_list_cmd = on_command(
    "vrcgil",
    aliases={"vrc邀请列表"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    group_invites_list_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@group_invites_list_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在获取群组邀请列表：{arg}")
    try:
        client = await get_client(session_id)
        invites = await get_group_invites(client, arg, n=20)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if not invites:
        await matcher.finish("该群组没有发送的邀请")

    msg = f"群组邀请列表 (共 {len(invites)} 个)：\n\n"
    for i, invite in enumerate(invites[:20], 1):
        msg += f"{i}. 用户 ID: {invite.get('user_id', '未知')}\n"
        msg += f"   邀请时间：{format_datetime(invite.get('created_at'))}\n\n"

    await matcher.finish(msg)


# region 处理群组加入请求
process_join_request_cmd = on_command(
    "vrcgpjr",
    aliases={"vrc处理请求", "vrc审批入群"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    process_join_request_cmd,
    lambda matcher: "请发送群组 ID 用户 ID 和 操作 (accept/reject)，用空格分隔",  # noqa: ARG005
)


@process_join_request_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject(
            "请发送群组 ID 用户 ID 和 操作 (accept/reject)，用空格分隔",
        )

    parts = arg.split()
    if len(parts) != 3:
        await matcher.reject("格式错误，请发送 群组 ID 用户 ID accept/reject")

    group_id, user_id, action = parts
    accept = action.lower() == "accept"

    logger.info(f"正在处理群组加入请求：{group_id} - {user_id} - {action}")
    try:
        client = await get_client(session_id)
        result = await respond_to_group_join_request(client, group_id, user_id, accept)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        action_text = "接受" if accept else "拒绝"
        await matcher.finish(f"已{action_text}用户 {user_id} 的加入请求")
    else:
        await matcher.finish("处理请求失败")


# region 取消群组加入请求
cancel_join_request_cmd = on_command(
    "vrcgcjr",
    aliases={"vrc取消请求"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    cancel_join_request_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@cancel_join_request_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在取消群组加入请求：{arg}")
    try:
        client = await get_client(session_id)
        result = await cancel_group_join_request(client, arg)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish("已取消群组加入请求")
    else:
        await matcher.finish("取消请求失败")


# region 群组封禁列表
group_bans_cmd = on_command(
    "vrcgb",
    aliases={"vrc封禁列表"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    group_bans_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@group_bans_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在获取群组封禁列表：{arg}")
    try:
        client = await get_client(session_id)
        bans = await get_group_bans(client, arg, n=20)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if not bans:
        await matcher.finish("该群组没有封禁记录")

    msg = f"群组封禁列表 (共 {len(bans)} 个)：\n\n"
    for i, ban in enumerate(bans[:20], 1):
        msg += f"{i}. 用户 ID: {ban.get('user_id', '未知')}\n"
        msg += f"   封禁时间：{format_datetime(ban.get('created_at'))}\n"
        msg += f"   原因：{ban.get('reason', '无')}\n\n"

    await matcher.finish(msg)


# region 封禁群组成员
ban_member_cmd = on_command(
    "vrcgbm",
    aliases={"vrc封禁成员"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    ban_member_cmd,
    lambda matcher: "请发送群组 ID 和 用户 ID，用空格分隔",  # noqa: ARG005
)


@ban_member_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID 和 用户 ID，用空格分隔")

    parts = arg.split()
    if len(parts) != 2:
        await matcher.reject("格式错误，请发送 群组 ID 用户 ID")

    group_id, user_id = parts
    logger.info(f"正在封禁群组成员：{group_id} - {user_id}")
    try:
        client = await get_client(session_id)
        result = await ban_group_member(client, group_id, user_id)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish(f"已封禁用户 {user_id}")
    else:
        await matcher.finish("封禁成员失败")


# region 解除封禁群组成员
unban_member_cmd = on_command(
    "vrcgub",
    aliases={"vrc解除封禁"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    unban_member_cmd,
    lambda matcher: "请发送群组 ID 和 用户 ID，用空格分隔",  # noqa: ARG005
)


@unban_member_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID 和 用户 ID，用空格分隔")

    parts = arg.split()
    if len(parts) != 2:
        await matcher.reject("格式错误，请发送 群组 ID 用户 ID")

    group_id, user_id = parts
    logger.info(f"正在解除封禁群组成员：{group_id} - {user_id}")
    try:
        client = await get_client(session_id)
        result = await unban_group_member(client, group_id, user_id)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if result:
        await matcher.finish(f"已解除封禁用户 {user_id}")
    else:
        await matcher.finish("解除封禁失败")


# region 群组审计日志
group_audit_logs_cmd = on_command(
    "vrcgal",
    aliases={"vrc审计日志"},
    rule=rule_enable,
    priority=20,
)


register_arg_got_handlers(
    group_audit_logs_cmd,
    lambda matcher: "请发送群组 ID",  # noqa: ARG005
)


@group_audit_logs_cmd.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    arg: str = ArgPlainText(KEY_ARG),
):
    arg = arg.strip()
    if not arg:
        await matcher.reject("请发送群组 ID")

    logger.info(f"正在获取群组审计日志：{arg}")
    try:
        client = await get_client(session_id)
        logs = await get_group_audit_logs(client, arg, n=20)
    except Exception as e:
        await handle_error(matcher, e)
        return
    if not logs:
        await matcher.finish("该群组没有审计日志")

    msg = f"群组审计日志 (共 {len(logs)} 条)：\n\n"
    for i, log in enumerate(logs[:20], 1):
        msg += f"{i}. 操作：{log.get('action', '未知')}\n"
        msg += f"   执行者：{log.get('actor', {}).get('display_name', '未知')}\n"
        msg += f"   目标：{log.get('target', {}).get('display_name', '未知')}\n"
        msg += f"   时间：{format_datetime(log.get('created_at'))}\n\n"

    await matcher.finish(msg)


# region 群组帮助
group_help = on_command(
    "vrcgrouphelp",
    aliases={"vrc群组帮助"},
    rule=rule_enable,
    priority=20,
)


@group_help.handle()
async def _(matcher: Matcher):
    msg = """--------vrc群组指令--------
【基础查询】
1、【vrc搜索群组】【关键词】| 搜索群组
2、【vrc群组信息】【群组 ID/名称】| 查看群组详情
3、【vrc群组成员】【群组 ID】| 查看成员列表
4、【vrc群组角色】【群组 ID】| 查看角色列表
5、【vrc群组公告】【群组 ID】| 查看公告列表
6、【vrc群组帖子】【群组 ID】| 查看帖子列表
7、【vrc群组画廊】【群组 ID】| 查看画廊
8、【vrc群组实例】【群组 ID】| 查看群组实例
9、【vrc群组权限】【群组 ID】| 查看权限
10、【vrc我的群组信息】【群组 ID】| 查看我的成员信息
11、【vrc邀请列表】【群组 ID】| 查看发出的邀请
12、【vrc封禁列表】【群组 ID】| 查看封禁列表
13、【vrc审计日志】【群组 ID】| 查看审计日志

【加入/离开】
14、【vrc加入群组】【群组 ID】| 申请加入群组
15、【vrc离开群组】【群组 ID】| 离开群组
16、【vrc取消请求】【群组 ID】| 取消加入请求

【成员管理】
17、【vrc踢出成员】【群组 ID 用户 ID】| 踢出成员
18、【vrc添加成员角色】【群组 ID 用户 ID 角色 ID】| 添加角色
19、【vrc移除成员角色】【群组 ID 用户 ID 角色 ID】| 移除角色
20、【vrc封禁成员】【群组 ID 用户 ID】| 封禁成员
21、【vrc解除封禁】【群组 ID 用户 ID】| 解除封禁
22、【vrc更新群组代表】【群组 ID】| 设置代表群组

【邀请管理】
23、【vrc邀请用户】【群组 ID 用户 ID】| 邀请用户入群
24、【vrc删除邀请】【群组 ID 用户 ID】| 删除群组邀请

【请求管理】
25、【vrc处理请求】【群组 ID 用户 ID accept/reject】| 审批入群请求

【公告/帖子管理】
26、【vrc创建公告】【群组 ID 标题 内容】| 创建公告
27、【vrc删除公告】【群组 ID 公告 ID】| 删除公告
28、【vrc创建帖子】【群组 ID 标题 内容】| 创建帖子
29、【vrc删除帖子】【群组 ID 帖子 ID】| 删除帖子"""
    await matcher.finish(msg)
