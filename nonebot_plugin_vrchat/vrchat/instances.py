from typing import TYPE_CHECKING, Awaitable, Optional, cast

from nonebot.utils import run_sync
from vrchatapi import ApiClient, InstancesApi

if TYPE_CHECKING:
    from vrchatapi.models import Instance


async def get_instance(
    client: ApiClient,
    world_id: str,
    instance_id: str,
) -> dict:
    """获取实例信息

    Args:
        client: ApiClient 实例
        world_id: 世界 ID
        instance_id: 实例 ID

    Returns:
        实例信息
    """
    api = InstancesApi(client)
    result = await cast(
        "Awaitable[Instance]",
        run_sync(api.get_instance)(
            world_id=world_id,
            instance_id=instance_id,
        ),
    )
    return result.to_dict() if result else {}


async def create_instance(
    client: ApiClient,
    create_instance_request: dict,
) -> dict:
    """创建新实例

    Args:
        client: ApiClient 实例
        create_instance_request: 创建实例请求对象

    Returns:
        创建的实例信息
    """
    from vrchatapi.models import CreateInstanceRequest

    api = InstancesApi(client)
    result = await cast(
        "Awaitable[Instance]",
        run_sync(api.create_instance)(
            create_instance_request=CreateInstanceRequest(**create_instance_request),
        ),
    )
    return result.to_dict() if result else {}


async def close_instance(
    client: ApiClient,
    world_id: str,
    instance_id: str,
) -> bool:
    """关闭实例

    Args:
        client: ApiClient 实例
        world_id: 世界 ID
        instance_id: 实例 ID

    Returns:
        是否关闭成功
    """
    api = InstancesApi(client)
    await run_sync(api.close_instance)(
        world_id=world_id,
        instance_id=instance_id,
    )
    return True


async def get_instance_by_short_name(
    client: ApiClient,
    short_name: str,
) -> dict:
    """通过短名称获取实例信息

    Args:
        client: ApiClient 实例
        short_name: 实例短名称

    Returns:
        实例信息
    """
    api = InstancesApi(client)
    result = await cast(
        "Awaitable[Instance]",
        run_sync(api.get_instance_by_short_name)(short_name=short_name),
    )
    return result.to_dict() if result else {}


async def get_short_name(
    client: ApiClient,
    world_id: str,
    instance_id: str,
) -> Optional[str]:
    """获取实例短名称

    Args:
        client: ApiClient 实例
        world_id: 世界 ID
        instance_id: 实例 ID

    Returns:
        短名称
    """
    api = InstancesApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_short_name)(
            world_id=world_id,
            instance_id=instance_id,
        ),
    )
    return result.get("shortName") if result else None


async def get_recent_locations(
    client: ApiClient,
    user_id: str,
    n: int = 10,
) -> list[str]:
    """获取用户最近访问的位置列表

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        n: 返回数量，默认 10

    Returns:
        位置列表
    """
    api = InstancesApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_recent_locations)(userId=user_id, n=n),
    )
    return result if result else []
