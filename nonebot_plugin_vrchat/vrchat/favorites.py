from collections.abc import AsyncIterable, Awaitable
from typing import TYPE_CHECKING, cast
from typing_extensions import Unpack

from nonebot.utils import run_sync
from vrchatapi import ApiClient, FavoritesApi

from .types import FavoriteGroupModel, FavoriteLimitsModel, FavoriteModel
from .utils import (
    IterPFKwargs,
    auto_parse_iterator_return,
    iter_pagination_func,
)

if TYPE_CHECKING:
    from vrchatapi.models import (
        AddFavoriteRequest,
        Favorite,
        FavoriteGroup,
        FavoriteLimits,
        Success,
    )


async def add_favorite(
    client: ApiClient,
    add_favorite_request: "AddFavoriteRequest",
) -> "FavoriteGroup":
    """添加收藏项。

    参数:
        client (ApiClient): API 客户端实例。
        add_favorite_request (AddFavoriteRequest): 包含添加收藏请求数据的对象。

    返回:
        FavoriteGroup: 添加收藏后的结果。
    """
    api = FavoritesApi(client)
    return await cast(
        "Awaitable[FavoriteGroup]",
        run_sync(api.add_favorite)(add_favorite_request=add_favorite_request),
    )


async def remove_favorite(
    client: ApiClient,
    favorite_id: str,
) -> bool:
    """删除收藏项。

    参数:
        client (ApiClient): API 客户端实例。
        favorite_id (str): 收藏项 ID。

    返回:
        bool: 是否删除成功。
    """
    api = FavoritesApi(client)
    await run_sync(api.remove_favorite)(favorite_id=favorite_id)
    return True


async def clear_favorite_group(
    client: ApiClient,
    favorite_group_type: str,
    favorite_group_name: str,
    user_id: str,
) -> "Success":
    """清空收藏组。

    参数:
        client (ApiClient): API 客户端实例。
        favorite_group_type (str): 收藏组类型。
        favorite_group_name (str): 收藏组名称。
        user_id (str): 用户 ID。

    返回:
        Success: 操作结果。
    """
    api = FavoritesApi(client)
    return await cast(
        "Awaitable[Success]",
        run_sync(api.clear_favorite_group)(
            favorite_group_type=favorite_group_type,
            favorite_group_name=favorite_group_name,
            user_id=user_id,
        ),
    )


async def get_favorite_group(
    client: ApiClient,
    favorite_group_type: str,
    favorite_group_name: str,
    user_id: str,
) -> "FavoriteGroup":
    """获取收藏组信息。

    参数:
        client (ApiClient): API 客户端实例。
        favorite_group_type (str): 收藏组类型。
        favorite_group_name (str): 收藏组名称。
        user_id (str): 用户 ID。

    返回:
        FavoriteGroup: 收藏组信息。
    """
    api = FavoritesApi(client)
    return await cast(
        "Awaitable[FavoriteGroup]",
        run_sync(api.get_favorite_group)(
            favorite_group_type=favorite_group_type,
            favorite_group_name=favorite_group_name,
            user_id=user_id,
        ),
    )


async def update_favorite_group(
    client: ApiClient,
    favorite_group_type: str,
    favorite_group_name: str,
    user_id: str,
    update_favorite_group_request: dict,
) -> "FavoriteGroup":
    """更新收藏组信息。

    参数:
        client (ApiClient): API 客户端实例。
        favorite_group_type (str): 收藏组类型。
        favorite_group_name (str): 收藏组名称。
        user_id (str): 用户 ID。
        update_favorite_group_request (dict): 更新请求数据。

    返回:
        FavoriteGroup: 更新后的收藏组信息。
    """
    from vrchatapi.models import UpdateFavoriteGroupRequest

    api = FavoritesApi(client)
    return await cast(
        "Awaitable[FavoriteGroup]",
        run_sync(api.update_favorite_group)(
            favorite_group_type=favorite_group_type,
            favorite_group_name=favorite_group_name,
            user_id=user_id,
            update_favorite_group_request=UpdateFavoriteGroupRequest(
                **update_favorite_group_request,
            ),
        ),
    )


def get_favorites(
    client: ApiClient,
    favorite_type: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[FavoriteModel]:
    """获取收藏列表。

    参数:
        client (ApiClient): API 客户端实例。
        favorite_type (str): 收藏类型（avatar/world）。
        pf_kwargs: 分页查询相关参数。

    返回:
        AsyncIterable[FavoriteModel]: 收藏列表的异步迭代器。
    """
    api = FavoritesApi(client)

    @auto_parse_iterator_return(FavoriteModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int) -> list["Favorite"]:
        return await cast(
            "Awaitable[list[Favorite]]",
            run_sync(api.get_favorites)(
                type=favorite_type,
                n=page_size,
                offset=offset,
            ),
        )

    return iterator()


def get_favorite_groups(
    client: ApiClient,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[FavoriteGroupModel]:
    """获取所有收藏组列表。

    参数:
        client (ApiClient): API 客户端实例。
        pf_kwargs: 分页查询相关参数。

    返回:
        AsyncIterable[FavoriteGroupModel]: 收藏组列表的异步迭代器。
    """
    api = FavoritesApi(client)

    @auto_parse_iterator_return(FavoriteGroupModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int) -> list["FavoriteGroup"]:
        return await cast(
            "Awaitable[list[FavoriteGroup]]",
            run_sync(api.get_favorite_groups)(
                n=page_size,
                offset=offset,
            ),
        )

    return iterator()


async def get_favorite_limits(client: ApiClient) -> FavoriteLimitsModel:
    """获取收藏限制信息。

    参数:
        client (ApiClient): API 客户端实例。

    返回:
        FavoriteLimitsModel: 收藏限制信息。
    """
    api = FavoritesApi(client)
    result = await cast(
        "Awaitable[FavoriteLimits]",
        run_sync(api.get_favorite_limits)(),
    )
    return FavoriteLimitsModel(**result.to_dict())
