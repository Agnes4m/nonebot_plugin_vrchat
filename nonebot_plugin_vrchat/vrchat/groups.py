from collections.abc import AsyncIterable
from typing import Awaitable, List, cast
from typing_extensions import Unpack

from nonebot.utils import run_sync
from vrchatapi import ApiClient, GroupsApi, JoinGroupRequest

from .types import (
    GroupAnnouncementModel,
    GroupInstanceModel,
    GroupMemberModel,
    GroupModel,
    GroupPermissionModel,
    GroupRoleModel,
    LimitedGroupModel,
)
from .utils import (
    IterPFKwargs,
    auto_parse_iterator_return,
    iter_pagination_func,
)


def search_groups(
    client: ApiClient,
    keyword: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[LimitedGroupModel]:
    """搜索群组"""
    api = GroupsApi(client)

    @auto_parse_iterator_return(LimitedGroupModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int):
        result = await cast(
            "Awaitable[list]",
            run_sync(api.search_groups)(query=keyword, offset=offset, n=page_size),
        )
        return result or []

    return iterator()


async def get_group(client: ApiClient, group_id: str) -> GroupModel:
    """获取群组信息"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_group)(group_id=group_id),
    )
    return GroupModel(**result.to_dict())


async def create_group(
    client: ApiClient,
    create_group_request: dict,
) -> GroupModel:
    """创建群组"""
    from vrchatapi.models import CreateGroupRequest

    api = GroupsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.create_group)(
            create_group_request=CreateGroupRequest(**create_group_request),
        ),
    )
    return (
        GroupModel(**result)
        if isinstance(result, dict)
        else GroupModel.model_validate({})
    )


async def update_group(
    client: ApiClient,
    group_id: str,
    update_group_request: dict,
) -> GroupModel:
    """更新群组信息"""
    from vrchatapi.models import UpdateGroupRequest

    api = GroupsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.update_group)(
            group_id=group_id,
            update_group_request=UpdateGroupRequest(**update_group_request),
        ),
    )
    return (
        GroupModel(**result)
        if isinstance(result, dict)
        else GroupModel.model_validate({})
    )


async def delete_group(client: ApiClient, group_id: str) -> bool:
    """删除群组"""
    api = GroupsApi(client)
    await run_sync(api.delete_group)(group_id=group_id)
    return True


async def get_group_members(
    client: ApiClient,
    group_id: str,
    n: int = 20,
    offset: int = 0,
) -> List[GroupMemberModel]:
    """获取群组成员列表"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_members)(
            group_id=group_id,
            n=n,
            offset=offset,
        ),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def get_group_roles(
    client: ApiClient,
    group_id: str,
) -> List[GroupRoleModel]:
    """获取群组角色列表"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_roles)(
            group_id=group_id,
        ),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def get_group_announcements(
    client: ApiClient,
    group_id: str,
) -> GroupAnnouncementModel:
    """获取群组公告"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_group_announcements)(
            group_id=group_id,
        ),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def join_group(client: ApiClient, group_id: str) -> bool:
    """加入群组"""
    api = GroupsApi(client)
    await run_sync(api.join_group)(
        group_id=group_id,
        confirm_override_block=True,
        join_group_request=JoinGroupRequest(),
    )
    return True


async def leave_group(client: ApiClient, group_id: str) -> bool:
    """离开群组"""
    api = GroupsApi(client)
    await run_sync(api.leave_group)(group_id=group_id)
    return True


async def get_group_invites(
    client: ApiClient,
    group_id: str,
    n: int = 20,
    offset: int = 0,
) -> List[GroupMemberModel]:
    """获取群组邀请列表"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_invites)(
            group_id=group_id,
            n=n,
            offset=offset,
        ),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def get_group_requests(
    client: ApiClient,
    group_id: str,
    n: int = 20,
    offset: int = 0,
) -> List[GroupMemberModel]:
    """获取群组请求列表"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_requests)(
            group_id=group_id,
            n=n,
            offset=offset,
        ),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def get_group_instances(
    client: ApiClient,
    group_id: str,
) -> List[GroupInstanceModel]:
    """获取群组实例列表"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_instances)(
            group_id=group_id,
        ),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def get_group_permissions(
    client: ApiClient,
    group_id: str,
) -> GroupPermissionModel:
    """获取群组权限信息"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_group_permissions)(group_id=group_id),
    )
    return result if isinstance(result, dict) else {}


async def kick_group_member(
    client: ApiClient,
    group_id: str,
    user_id: str,
) -> bool:
    """踢出群组成员"""
    api = GroupsApi(client)
    await run_sync(api.kick_group_member)(group_id=group_id, user_id=user_id)
    return True


async def add_member_role(
    client: ApiClient,
    group_id: str,
    user_id: str,
    role_id: str,
) -> bool:
    """给群组成员添加角色"""
    api = GroupsApi(client)
    await run_sync(api.add_member_role)(
        group_id=group_id,
        user_id=user_id,
        role_id=role_id,
    )
    return True


async def remove_member_role(
    client: ApiClient,
    group_id: str,
    user_id: str,
    role_id: str,
) -> bool:
    """从群组成员移除角色"""
    api = GroupsApi(client)
    await run_sync(api.remove_member_role)(
        group_id=group_id,
        user_id=user_id,
        role_id=role_id,
    )
    return True


async def create_group_announcement(
    client: ApiClient,
    group_id: str,
    title: str,
    text: str,
    image_url: str | None = None,
) -> dict:
    """创建群组公告"""
    from vrchatapi.models import CreateGroupAnnouncementRequest

    api = GroupsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.create_group_announcement)(
            group_id=group_id,
            create_group_announcement_request=CreateGroupAnnouncementRequest(
                title=title,
                text=text,
                image_url=image_url,
            ),
        ),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def delete_group_announcement(
    client: ApiClient,
    group_id: str,
    announcement_id: str,
) -> bool:
    """删除群组公告"""
    api = GroupsApi(client)
    await run_sync(api.delete_group_announcement)(
        group_id=group_id,
        announcement_id=announcement_id,
    )
    return True


async def create_group_post(
    client: ApiClient,
    group_id: str,
    title: str,
    text: str,
) -> dict:
    """创建群组帖子"""
    from vrchatapi.models import CreateGroupPostRequest

    api = GroupsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.create_group_post)(
            group_id=group_id,
            create_group_post_request=CreateGroupPostRequest(
                title=title,
                text=text,
            ),
        ),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def get_group_posts(
    client: ApiClient,
    group_id: str,
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取群组帖子列表"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_posts)(
            group_id=group_id,
            n=n,
            offset=offset,
        ),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def delete_group_post(
    client: ApiClient,
    group_id: str,
    post_id: str,
) -> bool:
    """删除群组帖子"""
    api = GroupsApi(client)
    await run_sync(api.delete_group_post)(group_id=group_id, post_id=post_id)
    return True


async def edit_group_post(
    client: ApiClient,
    group_id: str,
    post_id: str,
    title: str,
    text: str,
) -> dict:
    """编辑群组帖子"""
    from vrchatapi.models import UpdateGroupPostRequest

    api = GroupsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.edit_group_post)(
            group_id=group_id,
            post_id=post_id,
            update_group_post_request=UpdateGroupPostRequest(
                title=title,
                text=text,
            ),
        ),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def get_group_gallery(
    client: ApiClient,
    group_id: str,
) -> dict:
    """获取群组画廊信息"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_group_gallery)(group_id=group_id),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def get_group_gallery_images(
    client: ApiClient,
    group_id: str,
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取群组画廊图片列表"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_gallery_images)(
            group_id=group_id,
            n=n,
            offset=offset,
        ),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def add_group_gallery_image(
    client: ApiClient,
    group_id: str,
    file_id: str,
    description: str | None = None,
) -> dict:
    """添加群组画廊图片"""
    from vrchatapi.models import AddGroupGalleryImageRequest

    api = GroupsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.add_group_gallery_image)(
            group_id=group_id,
            add_group_gallery_image_request=AddGroupGalleryImageRequest(
                file_id=file_id,
                description=description,
            ),
        ),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def delete_group_gallery_image(
    client: ApiClient,
    group_id: str,
    image_id: str,
) -> bool:
    """删除群组画廊图片"""
    api = GroupsApi(client)
    await run_sync(api.delete_group_gallery_image)(
        group_id=group_id,
        image_id=image_id,
    )
    return True


async def delete_group_gallery(
    client: ApiClient,
    group_id: str,
) -> bool:
    """删除群组画廊"""
    api = GroupsApi(client)
    await run_sync(api.delete_group_gallery)(group_id=group_id)
    return True


async def invite_user_to_group(
    client: ApiClient,
    group_id: str,
    user_id: str,
) -> bool:
    """邀请用户加入群组"""
    from vrchatapi.models import GroupInviteRequest

    api = GroupsApi(client)
    await run_sync(api.invite_user_to_group)(
        group_id=group_id,
        group_invite_request=GroupInviteRequest(user_id=user_id),
    )
    return True


async def delete_group_invite(
    client: ApiClient,
    group_id: str,
    user_id: str,
) -> bool:
    """删除群组邀请"""
    api = GroupsApi(client)
    await run_sync(api.delete_group_invite)(group_id=group_id, user_id=user_id)
    return True


async def respond_to_group_join_request(
    client: ApiClient,
    group_id: str,
    user_id: str,
    accept: bool,
) -> bool:
    """响应群组加入请求"""
    api = GroupsApi(client)
    await run_sync(api.respond_to_group_join_request)(
        group_id=group_id,
        user_id=user_id,
        accept=accept,
    )
    return True


async def cancel_group_join_request(
    client: ApiClient,
    group_id: str,
) -> bool:
    """取消群组加入请求"""
    api = GroupsApi(client)
    await run_sync(api.cancel_group_join_request)(group_id=group_id)
    return True


async def get_group_bans(
    client: ApiClient,
    group_id: str,
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取群组禁止列表"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_bans)(
            group_id=group_id,
            n=n,
            offset=offset,
        ),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def ban_group_member(
    client: ApiClient,
    group_id: str,
    user_id: str,
) -> bool:
    """禁止群组成员"""
    api = GroupsApi(client)
    await run_sync(api.ban_group_member)(group_id=group_id, user_id=user_id)
    return True


async def unban_group_member(
    client: ApiClient,
    group_id: str,
    user_id: str,
) -> bool:
    """解除禁止群组成员"""
    api = GroupsApi(client)
    await run_sync(api.unban_group_member)(group_id=group_id, user_id=user_id)
    return True


async def get_group_audit_logs(
    client: ApiClient,
    group_id: str,
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取群组审计日志"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_audit_logs)(
            group_id=group_id,
            n=n,
            offset=offset,
        ),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def update_group_representation(
    client: ApiClient,
    group_id: str,
    represent: bool,
) -> bool:
    """更新群组代表身份"""
    api = GroupsApi(client)
    await run_sync(api.update_group_representation)(
        group_id=group_id,
        represent=represent,
    )
    return True


async def get_my_group_member(
    client: ApiClient,
    group_id: str,
) -> dict:
    """获取当前用户在群组中的成员信息"""
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_my_group_member)(group_id=group_id),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}
