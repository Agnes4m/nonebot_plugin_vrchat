from collections.abc import AsyncIterable, Awaitable
from typing import TYPE_CHECKING, cast
from typing_extensions import Unpack

from loguru import logger
from nonebot.utils import run_sync
from vrchatapi import ApiClient, FavoritesApi

from .types import FavoriteGroupModel, FavoriteLimitsModel, FavoriteModel
from .utils import IterPFKwargs, auto_parse_iterator_return, iter_pagination_func

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
    api = FavoritesApi(client)
    return await cast(
        "Awaitable[FavoriteGroup]",
        run_sync(api.add_favorite)(add_favorite_request=add_favorite_request),
    )


async def remove_favorite(client: ApiClient, favorite_id: str) -> "Success":
    api = FavoritesApi(client)
    return await cast(
        "Awaitable[Success]",
        run_sync(api.remove_favorite)(favorite_id=favorite_id),
    )


async def clear_favorite_group(
    client: ApiClient,
    favorite_group_type: str,
    favorite_group_name: str,
    user_id: str,
) -> "Success":
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
    tag: str = "",
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[FavoriteModel]:
    api = FavoritesApi(client)

    @auto_parse_iterator_return(FavoriteModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int) -> list["Favorite"]:
        result = await cast(
            "Awaitable[list[Favorite]]",
            run_sync(api.get_favorites)(
                type=favorite_type,
                n=page_size,
                offset=offset,
                tag=tag,
            ),
        )
        if result:
            logger.debug(f"[get_favorites] 第一条：{result[0].to_dict()}")
        return result

    return iterator()


def get_favorite_groups(
    client: ApiClient,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[FavoriteGroupModel]:
    api = FavoritesApi(client)

    @auto_parse_iterator_return(FavoriteGroupModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int) -> list["FavoriteGroup"]:
        return await cast(
            "Awaitable[list[FavoriteGroup]]",
            run_sync(api.get_favorite_groups)(n=page_size, offset=offset),
        )

    return iterator()


async def get_favorite_limits(client: ApiClient) -> FavoriteLimitsModel:
    api = FavoritesApi(client)
    result = await cast(
        "Awaitable[FavoriteLimits]",
        run_sync(api.get_favorite_limits)(),
    )
    return FavoriteLimitsModel(**result.to_dict())
