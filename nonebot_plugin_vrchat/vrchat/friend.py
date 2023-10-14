from typing import AsyncIterable, Awaitable, List, cast
from typing_extensions import Unpack

from nonebot.utils import run_sync
from vrchatapi import ApiClient, FriendsApi, LimitedUser

from .types import LimitedUserModel
from .utils import IterPFKwargs, auto_parse_iterator_return, iter_pagination_func


def get_friends(
    client: ApiClient,
    offline: bool,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[LimitedUserModel]:
    """
    获取在线或离线的好友列表

    Args:
        client: ApiClient 实例
        offline: 是否仅获取离线玩家，为 `False` 时仅获取在线玩家
        pf_kwargs: 分页查询相关参数

    Returns:
        获取好友列表的异步迭代器
    """

    api = FriendsApi(client)

    @auto_parse_iterator_return(LimitedUserModel)
    @iter_pagination_func(**pf_kwargs)
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
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[LimitedUserModel]:
    """
    获取所有好友列表

    Args:
        client: ApiClient 实例
        pf_kwargs: 分页查询相关参数

    Returns:
        获取好友列表的异步迭代器
    """

    async for x in get_friends(client, offline=False, **pf_kwargs):
        yield x
    async for x in get_friends(client, offline=True, **pf_kwargs):
        yield x
