from typing import AsyncIterable, Awaitable, List, cast
from typing_extensions import Unpack

from nonebot.utils import run_sync
from vrchatapi import ApiClient, FriendsApi
from vrchatapi.models import FriendStatus, LimitedUser, Notification, Success

from .types import LimitedUserModel
from .utils import IterPFKwargs, auto_parse_iterator_return, iter_pagination_func


async def delete_friend_request(
    client: ApiClient,
    user_id: str,
):
    """
    删除指定用户的好友请求。

    参数:
    - client (ApiClient): API客户端实例，用于与VRChat交互。
    - user_id (str): 要删除好友请求的目标用户的唯一标识符。

    返回值:
    - Success: 如果操作成功，则返回一个Success对象。
    """
    api = FriendsApi(client)
    return await cast(
        Awaitable[Success],
        run_sync(api.delete_friend_request)(user_id=user_id),
    )


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


async def get_friend_status(
    client: ApiClient,
    user_id: str,
) -> FriendStatus:
    """
    获取是否是给定用户的好友，是否有传出的好友请求，以及是否有传入的好友请求信息。

    参数:
    client (ApiClient): API客户端实例，用于发起API请求
    user_id (str): 要查询的好友用户ID

    返回:
    FriendStatus: 好友状态对象，包含好友关系的状态信息
    """
    api = FriendsApi(client)
    return await cast(
        Awaitable[FriendStatus],
        run_sync(api.get_friend_status)(user_id=user_id),
    )


async def friend(
    client: ApiClient,
    user_id: str,
):
    """
    异步函数，用于发送好友请求。

    参数:
    client (ApiClient): API客户端实例。
    user_id (str): 用户ID。

    返回值:
    Notification: 返回一个Notification对象。
    """

    api = FriendsApi(client)
    return await cast(
        Awaitable[Notification],
        run_sync(api.friend)(user_id=user_id),
    )


async def unfriend(
    client: ApiClient,
    user_id: str,
):
    """
    取消好友关系。

    参数:
        client (ApiClient): API客户端实例。
        user_id (str): 要取消的好友的用户ID。

    返回值:
        Success: 表示操作成功的类型。
    """
    api = FriendsApi(client)
    return await cast(
        Awaitable[Success],
        run_sync(api.unfriend)(user_id=user_id),
    )
