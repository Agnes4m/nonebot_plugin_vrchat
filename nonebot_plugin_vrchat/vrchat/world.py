from typing import AsyncIterable, Awaitable, List, cast
from typing_extensions import Unpack

from nonebot.utils import run_sync
from vrchatapi import ApiClient, LimitedWorld, World, WorldsApi

from .types import LimitedWorldModel, WorldModel
from .utils import (
    IterPFKwargs,
    auto_parse_iterator_return,
    auto_parse_return,
    iter_pagination_func,
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

    Returns:
        获取搜索到世界的异步迭代器
    """

    api = WorldsApi(client)

    @auto_parse_iterator_return(LimitedWorldModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int) -> List[LimitedWorld]:
        return await cast(
            Awaitable[List[LimitedWorld]],
            run_sync(api.search_worlds)(search=keyword, n=page_size, offset=offset),
        )

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

    api = WorldsApi(client)
    return await cast(
        Awaitable[World],
        run_sync(api.get_world)(world_id=world_id),
    )
