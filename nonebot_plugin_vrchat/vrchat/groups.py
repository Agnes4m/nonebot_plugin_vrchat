from collections.abc import AsyncIterable
from typing import Awaitable, List, cast
from typing_extensions import Unpack

from nonebot.utils import run_sync
from vrchatapi import ApiClient, GroupsApi

from .types import GroupModel, LimitedGroupModel
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
    """搜索群组

    Args:
        client: ApiClient 实例
        keyword: 搜索关键词
        pf_kwargs: 分页查询相关参数

    Returns:
        搜索到的群组列表
    """
    api = GroupsApi(client)

    @auto_parse_iterator_return(LimitedGroupModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int):
        result = await cast(
            "Awaitable[list]",
            run_sync(api.search_groups)(search=keyword, n=page_size, offset=offset),
        )
        return result or []

    return iterator()


async def get_group(client: ApiClient, group_id: str) -> GroupModel:
    """获取群组信息

    Args:
        client: ApiClient 实例
        group_id: 群组 ID

    Returns:
        群组信息
    """
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_group)(group_id=group_id),
    )
    return (
        GroupModel(**result)
        if isinstance(result, dict)
        else GroupModel.model_validate({})
    )


async def create_group(
    client: ApiClient,
    create_group_request: dict,
) -> GroupModel:
    """创建群组

    Args:
        client: ApiClient 实例
        create_group_request: 创建群组请求对象

    Returns:
        创建的群组信息
    """
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
    """更新群组信息

    Args:
        client: ApiClient 实例
        group_id: 群组 ID
        update_group_request: 更新群组请求对象

    Returns:
        更新后的群组信息
    """
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
    """删除群组

    Args:
        client: ApiClient 实例
        group_id: 群组 ID

    Returns:
        是否删除成功
    """
    api = GroupsApi(client)
    await run_sync(api.delete_group)(group_id=group_id)
    return True


async def get_group_members(
    client: ApiClient,
    group_id: str,
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取群组成员列表

    Args:
        client: ApiClient 实例
        group_id: 群组 ID
        n: 返回数量
        offset: 偏移量

    Returns:
        成员列表
    """
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_members)(
            group_id=group_id,
            n=n,
            offset=offset,
        ),
    )
    return result if isinstance(result, list) else []


async def get_group_roles(
    client: ApiClient,
    group_id: str,
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取群组角色列表

    Args:
        client: ApiClient 实例
        group_id: 群组 ID
        n: 返回数量
        offset: 偏移量

    Returns:
        角色列表
    """
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_roles)(
            group_id=group_id,
            n=n,
            offset=offset,
        ),
    )
    return result if isinstance(result, list) else []


async def get_group_announcements(
    client: ApiClient,
    group_id: str,
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取群组公告列表

    Args:
        client: ApiClient 实例
        group_id: 群组 ID
        n: 返回数量
        offset: 偏移量

    Returns:
        公告列表
    """
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_announcements)(
            group_id=group_id,
            n=n,
            offset=offset,
        ),
    )
    return result if isinstance(result, list) else []


async def join_group(client: ApiClient, group_id: str) -> bool:
    """加入群组

    Args:
        client: ApiClient 实例
        group_id: 群组 ID

    Returns:
        是否加入成功
    """
    api = GroupsApi(client)
    await run_sync(api.join_group)(group_id=group_id)
    return True


async def leave_group(client: ApiClient, group_id: str) -> bool:
    """离开群组

    Args:
        client: ApiClient 实例
        group_id: 群组 ID

    Returns:
        是否离开成功
    """
    api = GroupsApi(client)
    await run_sync(api.leave_group)(group_id=group_id)
    return True


async def get_group_invites(
    client: ApiClient,
    group_id: str,
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取群组邀请列表

    Args:
        client: ApiClient 实例
        group_id: 群组 ID
        n: 返回数量
        offset: 偏移量

    Returns:
        邀请列表
    """
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_invites)(
            group_id=group_id,
            n=n,
            offset=offset,
        ),
    )
    return result if isinstance(result, list) else []


async def get_group_requests(
    client: ApiClient,
    group_id: str,
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取群组请求列表

    Args:
        client: ApiClient 实例
        group_id: 群组 ID
        n: 返回数量
        offset: 偏移量

    Returns:
        请求列表
    """
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_requests)(
            group_id=group_id,
            n=n,
            offset=offset,
        ),
    )
    return result if isinstance(result, list) else []


async def get_group_instances(
    client: ApiClient,
    group_id: str,
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取群组实例列表

    Args:
        client: ApiClient 实例
        group_id: 群组 ID
        n: 返回数量
        offset: 偏移量

    Returns:
        实例列表
    """
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_group_instances)(
            group_id=group_id,
            n=n,
            offset=offset,
        ),
    )
    return result if isinstance(result, list) else []


async def get_group_permissions(client: ApiClient, group_id: str) -> dict:
    """获取群组权限信息

    Args:
        client: ApiClient 实例
        group_id: 群组 ID

    Returns:
        权限信息
    """
    api = GroupsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_group_permissions)(group_id=group_id),
    )
    return result if isinstance(result, dict) else {}
