from collections.abc import AsyncIterable, Awaitable
from typing import TYPE_CHECKING, cast
from typing_extensions import Unpack

from nonebot.utils import run_sync
from vrchatapi import ApiClient, Avatar, AvatarsApi, LimitedWorld

from .types import AvatarModel, AvatarStyleModel, LimitedAvatarModel
from .utils import (
    IterPFKwargs,
    auto_parse_iterator_return,
    auto_parse_return,
    iter_pagination_func,
    user_agent,
)

if TYPE_CHECKING:
    from vrchatapi.models import (
        CreateAvatarRequest,
        UpdateAvatarRequest,
    )


def search_avatars(
    client: ApiClient,
    keyword: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[LimitedAvatarModel]:
    """
    搜索头像

    Args:
        client: ApiClient 实例
        keyword: 搜索关键词
        pf_kwargs: 分页查询相关参数

    Returns:
        获取搜索到头像的异步迭代器
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)

    @auto_parse_iterator_return(LimitedAvatarModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int) -> list[LimitedWorld]:
        return await cast(
            "Awaitable[list[LimitedWorld]]",
            run_sync(api.search_avatars)(search=keyword, n=page_size, offset=offset),
        )

    return iterator()


@auto_parse_return(AvatarModel)
async def get_avatar(client: ApiClient, avatar_id: str) -> Avatar:
    """
    通过头像 ID 获取头像信息

    Args:
        client: ApiClient 实例
        avatar_id: 头像 ID

    Returns:
        头像信息
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)
    return await cast(
        "Awaitable[Avatar]",
        run_sync(api.get_avatar)(avatar_id=avatar_id),
    )


@auto_parse_return(AvatarModel)
async def get_own_avatar(client: ApiClient, user_id: str) -> Avatar:
    """
    获取当前用户装备的头像信息

    Args:
        client: ApiClient 实例

    Returns:
        当前用户装备的头像信息
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)
    return await cast(
        "Awaitable[Avatar]",
        run_sync(api.get_own_avatar)(user_id=user_id),
    )


@auto_parse_return(AvatarModel)
async def create_avatar(
    client: ApiClient,
    create_avatar_request: "CreateAvatarRequest",
) -> Avatar:
    """
    创建新头像

    Args:
        client: ApiClient 实例
        create_avatar_request: 创建头像请求对象

    Returns:
        创建的头像信息
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)
    return await cast(
        "Awaitable[Avatar]",
        run_sync(api.create_avatar)(create_avatar_request=create_avatar_request),
    )


@auto_parse_return(AvatarModel)
async def update_avatar(
    client: ApiClient,
    avatar_id: str,
    update_avatar_request: "UpdateAvatarRequest",
) -> Avatar:
    """
    更新头像信息

    Args:
        client: ApiClient 实例
        avatar_id: 头像 ID
        update_avatar_request: 更新头像请求对象

    Returns:
        更新后的头像信息
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)
    return await cast(
        "Awaitable[Avatar]",
        run_sync(api.update_avatar)(
            avatar_id=avatar_id,
            update_avatar_request=update_avatar_request,
        ),
    )


async def delete_avatar(client: ApiClient, avatar_id: str) -> bool:
    """
    删除头像

    Args:
        client: ApiClient 实例
        avatar_id: 头像 ID

    Returns:
        是否删除成功
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)
    await run_sync(api.delete_avatar)(avatar_id=avatar_id)
    return True


async def select_avatar(client: ApiClient, avatar_id: str) -> bool:
    """
    装备头像

    Args:
        client: ApiClient 实例
        avatar_id: 要装备的头像 ID

    Returns:
        是否装备成功
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)
    await run_sync(api.select_avatar)(avatar_id=avatar_id)
    return True


async def select_fallback_avatar(client: ApiClient, avatar_id: str) -> bool:
    """
    设置备用头像

    Args:
        client: ApiClient 实例
        avatar_id: 要设置的备用头像 ID

    Returns:
        是否设置成功
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)
    await run_sync(api.select_fallback_avatar)(avatar_id=avatar_id)
    return True


def get_favorited_avatars(
    client: ApiClient,
    user_id: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[LimitedAvatarModel]:
    """
    获取用户收藏的头像列表

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        pf_kwargs: 分页查询相关参数

    Returns:
        获取收藏头像列表的异步迭代器
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)

    @auto_parse_iterator_return(LimitedAvatarModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int) -> list[LimitedWorld]:
        return await cast(
            "Awaitable[list[LimitedWorld]]",
            run_sync(api.get_favorited_avatars)(
                userId=user_id,
                n=page_size,
                offset=offset,
            ),
        )

    return iterator()


async def get_avatar_styles(client: ApiClient) -> list[AvatarStyleModel]:
    """
    获取所有可用的头像风格

    Args:
        client: ApiClient 实例

    Returns:
        头像风格列表
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)
    styles = await cast(
        "Awaitable[dict]",
        run_sync(api.get_avatar_styles)(),
    )
    # AvatarStyles 可能没有 styles 属性，直接返回列表
    if isinstance(styles, dict):
        styles_list = styles.get("styles", [])
        return [AvatarStyleModel(**s) for s in styles_list] if styles_list else []
    return []


async def get_impostor_queue_stats(client: ApiClient) -> dict:
    """
    获取 impostor 队列统计信息

    Args:
        client: ApiClient 实例

    Returns:
        impostor 队列统计信息
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_impostor_queue_stats)(),
    )
    return result if isinstance(result, dict) else {}


async def enqueue_impostor(client: ApiClient, avatar_id: str) -> bool:
    """
    将头像加入 impostor 队列

    Args:
        client: ApiClient 实例
        avatar_id: 头像 ID

    Returns:
        是否加入成功
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)
    await run_sync(api.enqueue_impostor)(avatar_id=avatar_id)
    return True


async def delete_impostor(client: ApiClient, avatar_id: str) -> bool:
    """
    从 impostor 队列中删除头像

    Args:
        client: ApiClient 实例
        avatar_id: 头像 ID

    Returns:
        是否删除成功
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)
    await run_sync(api.delete_impostor)(avatar_id=avatar_id)
    return True


def get_licensed_avatars(
    client: ApiClient,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[LimitedAvatarModel]:
    """
    获取已授权的头像列表

    Args:
        client: ApiClient 实例
        pf_kwargs: 分页查询相关参数

    Returns:
        获取已授权头像列表的异步迭代器
    """
    client.user_agent = user_agent
    api = AvatarsApi(client)

    @auto_parse_iterator_return(LimitedAvatarModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int) -> list[LimitedWorld]:
        return await cast(
            "Awaitable[list[LimitedWorld]]",
            run_sync(api.get_licensed_avatars)(n=page_size, offset=offset),
        )

    return iterator()
