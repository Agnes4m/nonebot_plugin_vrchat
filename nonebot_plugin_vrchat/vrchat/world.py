from typing import AsyncIterator, Awaitable, List, cast

from nonebot.utils import run_sync
from vrchatapi import ApiClient, LimitedWorld, World, WorldsApi

from .types import LimitedWorldModel, WorldModel
from .utils import auto_parse_iterator_return, auto_parse_return, iter_pagination_func


def search_worlds(
    client: ApiClient,
    keyword: str,
    page_size: int = 10,
    offset: int = 0,
) -> AsyncIterator[LimitedWorldModel]:
    api = WorldsApi(client)

    @auto_parse_iterator_return(LimitedWorldModel)
    @iter_pagination_func(page_size=page_size, offset=offset)
    async def iterator(page_size: int, offset: int) -> List[LimitedWorld]:
        return await cast(
            Awaitable[List[LimitedWorld]],
            run_sync(api.search_worlds)(search=keyword, n=page_size, offset=offset),
        )

    return iterator()


@auto_parse_return(WorldModel)
async def get_world(client: ApiClient, world_id: str) -> World:
    api = WorldsApi(client)
    return await cast(
        Awaitable[World],
        run_sync(api.get_world)(world_id=world_id),
    )
