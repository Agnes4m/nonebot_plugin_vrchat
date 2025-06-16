from typing import Awaitable, cast

from nonebot.utils import run_sync
from vrchatapi import ApiClient, FavoritesApi
from vrchatapi.models import AddFavoriteRequest, FavoriteType, Success


async def add_favorite(
    client: ApiClient,
    add_favorite_request: AddFavoriteRequest,
) -> FavoriteType:
    """添加收藏项。

    参数:
        client (ApiClient): API客户端实例。
        add_favorite_request (AddFavoriteRequest): 包含添加收藏请求数据的对象。

    返回:
        FavoriteType: 添加收藏后的结果类型。
    """
    api = FavoritesApi(client)
    return await cast(
        Awaitable[FavoriteType],
        run_sync(api.add_favorite)(add_favorite_request=add_favorite_request),
    )


async def clear_favorite_group(
    client: ApiClient,
    favorite_group_type: str,
    favorite_group_name: str,
    user_id: str,
) -> Success:
    api = FavoritesApi(client)
    return await cast(
        Awaitable[Success],
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
) -> Success:
    api = FavoritesApi(client)
    return await cast(
        Awaitable[Success],
        run_sync(api.get_favorite_group)(
            favorite_group_type=favorite_group_type,
            favorite_group_name=favorite_group_name,
            user_id=user_id,
        ),
    )
