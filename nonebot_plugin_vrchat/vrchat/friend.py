import asyncio
from typing import AsyncIterator, Awaitable, List, cast

from nonebot.utils import run_sync
from vrchatapi import ApiClient, FriendsApi, LimitedUser

from .types import LimitedUserModel
from .utils import auto_parse_iterator_return, iter_pagination_func


def get_friends(
    client: ApiClient,
    offline: bool,
    page_size: int = 100,
    offset: int = 0,
) -> AsyncIterator[LimitedUserModel]:
    api = FriendsApi(client)

    @auto_parse_iterator_return(LimitedUserModel)
    @iter_pagination_func(page_size=page_size, offset=offset)
    async def iterator(page_size: int, offset: int) -> List[LimitedUser]:
        return await cast(
            Awaitable[List[LimitedUser]],
            run_sync(api.get_friends)(
                offset=offset,
                n=page_size,
                offline=str(offline).lower(),
            ),
        )

    return iterator()


async def get_all_friends(
    client: ApiClient,
    page_size: int = 100,
    offset: int = 0,
) -> AsyncIterator[LimitedUserModel]:
    async for x in get_friends(
        client,
        offline=False,
        page_size=page_size,
        offset=offset,
    ):
        yield x

    async for x in get_friends(
        client,
        offline=True,
        page_size=page_size,
        offset=offset,
    ):
        yield x
        await asyncio.sleep(0.5)
