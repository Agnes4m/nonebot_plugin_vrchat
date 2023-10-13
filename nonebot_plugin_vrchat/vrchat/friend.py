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
    """这个函数创建了一个异步迭代器，它可以使用给定的API客户端去获取在线好友。参数offline用来判断是否包含离线好友，page_size和offset用于分页。这个函数内部定义了一个名为iterator的生成器函数，该函数通过调用FriendsApi的get_friends方法获取好友列表。"""
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
    """这个函数是对get_friends函数的封装，它创建了一个异步迭代器，该迭代器可以交替地从在线和离线好友中获取数据。对于每个在线好友，它立即返回，但是对于每个离线好友，它会延迟0.5秒。"""
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
