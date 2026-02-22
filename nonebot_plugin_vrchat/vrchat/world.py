from collections.abc import AsyncIterable, Awaitable
from typing import cast
from typing_extensions import Unpack

from nonebot.utils import run_sync
from vrchatapi import ApiClient, WorldsApi
from vrchatapi.models import World

from .types import LimitedWorldModel, WorldModel
from .utils import (
    IterPFKwargs,
    auto_parse_iterator_return,
    auto_parse_return,
    iter_pagination_func,
    user_agent,
)


def search_worlds(
    client: ApiClient,
    keyword: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[LimitedWorldModel]:
    """
    搜索世界

    Args:
        client: ApiClient 实例
        keyword: 搜索关键词
        pf_kwargs: 分页查询相关参数

    Returns:
        获取搜索到世界的异步迭代器
    """
    client.user_agent = user_agent
    api = WorldsApi(client)

    @auto_parse_iterator_return(LimitedWorldModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int):
        result = await cast(
            "Awaitable[list]",
            run_sync(api.search_worlds)(search=keyword, n=page_size, offset=offset),
        )
        return result or []

    return iterator()


@auto_parse_return(WorldModel)
async def get_world(client: ApiClient, world_id: str) -> World:
    """
    通过世界 ID 获取世界信息

    Args:
        client: ApiClient 实例
        world_id: 世界 ID

    Returns:
        世界信息
    """
    client.user_agent = user_agent
    api = WorldsApi(client)
    return await cast(
        "Awaitable[World]",
        run_sync(api.get_world)(world_id=world_id),
    )


@auto_parse_return(WorldModel)
async def create_world(
    client: ApiClient,
    create_world_request: dict,
) -> World:
    """
    创建新世界

    Args:
        client: ApiClient 实例
        create_world_request: 创建世界请求对象

    Returns:
        创建的世界信息
    """
    from vrchatapi.models import CreateWorldRequest

    client.user_agent = user_agent
    api = WorldsApi(client)
    return await cast(
        "Awaitable[World]",
        run_sync(api.create_world)(
            create_world_request=CreateWorldRequest(**create_world_request),
        ),
    )


@auto_parse_return(WorldModel)
async def update_world(
    client: ApiClient,
    world_id: str,
    update_world_request: dict,
) -> World:
    """
    更新世界信息

    Args:
        client: ApiClient 实例
        world_id: 世界 ID
        update_world_request: 更新世界请求对象

    Returns:
        更新后的世界信息
    """
    from vrchatapi.models import UpdateWorldRequest

    client.user_agent = user_agent
    api = WorldsApi(client)
    return await cast(
        "Awaitable[World]",
        run_sync(api.update_world)(
            world_id=world_id,
            update_world_request=UpdateWorldRequest(**update_world_request),
        ),
    )


async def delete_world(client: ApiClient, world_id: str) -> bool:
    """
    删除世界

    Args:
        client: ApiClient 实例
        world_id: 世界 ID

    Returns:
        是否删除成功
    """
    client.user_agent = user_agent
    api = WorldsApi(client)
    await run_sync(api.delete_world)(world_id=world_id)
    return True


async def publish_world(
    client: ApiClient,
    world_id: str,
    version: int = 1,
) -> bool:
    """
    发布世界

    Args:
        client: ApiClient 实例
        world_id: 世界 ID
        version: 版本号

    Returns:
        是否发布成功
    """
    client.user_agent = user_agent
    api = WorldsApi(client)
    await run_sync(api.publish_world)(world_id=world_id, version=version)
    return True


async def unpublish_world(client: ApiClient, world_id: str) -> bool:
    """
    取消发布世界

    Args:
        client: ApiClient 实例
        world_id: 世界 ID

    Returns:
        是否取消发布成功
    """
    client.user_agent = user_agent
    api = WorldsApi(client)
    await run_sync(api.unpublish_world)(world_id=world_id)
    return True


async def get_world_instance(
    client: ApiClient,
    world_id: str,
    instance_id: str,
) -> dict:
    """
    获取世界实例信息

    Args:
        client: ApiClient 实例
        world_id: 世界 ID
        instance_id: 实例 ID

    Returns:
        世界实例信息
    """
    client.user_agent = user_agent
    api = WorldsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_world_instance)(
            world_id=world_id,
            instance_id=instance_id,
        ),
    )
    return result if isinstance(result, dict) else {}


async def get_world_publish_status(
    client: ApiClient,
    world_id: str,
) -> dict:
    """
    获取世界发布状态

    Args:
        client: ApiClient 实例
        world_id: 世界 ID

    Returns:
        世界发布状态
    """
    client.user_agent = user_agent
    api = WorldsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_world_publish_status)(world_id=world_id),
    )
    return result if isinstance(result, dict) else {}


async def get_world_metadata(
    client: ApiClient,
    world_id: str,
) -> WorldModel:
    """
    获取世界元数据

    Args:
        client: ApiClient 实例
        world_id: 世界 ID

    Returns:
        世界元数据
    """
    client.user_agent = user_agent
    api = WorldsApi(client)
    world = await cast(
        "Awaitable[dict]",
        run_sync(api.get_world_metadata)(world_id=world_id),
    )
    return (
        WorldModel(**world)
        if isinstance(world, dict)
        else WorldModel.model_validate({})
    )


async def check_user_persistence_exists(
    client: ApiClient,
    world_id: str,
    user_id: str,
) -> bool:
    """
    检查用户持久化数据是否存在

    Args:
        client: ApiClient 实例
        world_id: 世界 ID
        user_id: 用户 ID

    Returns:
        是否存在
    """
    client.user_agent = user_agent
    api = WorldsApi(client)
    return await cast(
        "Awaitable[bool]",
        run_sync(api.check_user_persistence_exists)(
            world_id=world_id,
            user_id=user_id,
        ),
    )


async def delete_user_persistence(
    client: ApiClient,
    world_id: str,
    user_id: str,
) -> bool:
    """
    删除用户持久化数据

    Args:
        client: ApiClient 实例
        world_id: 世界 ID
        user_id: 用户 ID

    Returns:
        是否删除成功
    """
    client.user_agent = user_agent
    api = WorldsApi(client)
    await run_sync(api.delete_user_persistence)(
        world_id=world_id,
        user_id=user_id,
    )
    return True


async def delete_all_user_persistence_data(
    client: ApiClient,
    user_id: str,
) -> bool:
    """
    删除所有用户持久化数据

    Args:
        client: ApiClient 实例
        user_id: 世界 ID

    Returns:
        是否删除成功
    """
    client.user_agent = user_agent
    api = WorldsApi(client)
    await run_sync(api.delete_all_user_persistence_data)(user_id=user_id)
    return True
