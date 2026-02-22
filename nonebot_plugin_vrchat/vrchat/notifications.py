from collections.abc import AsyncIterable, Awaitable
from typing import cast
from typing_extensions import Unpack

from nonebot.utils import run_sync
from vrchatapi import ApiClient, NotificationsApi, Success
from vrchatapi.models import Notification

from .types import NotificationModel
from .utils import (
    IterPFKwargs,
    auto_parse_iterator_return,
    iter_pagination_func,
)


def get_notifications(
    client: ApiClient,
    # n: int = 60,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[NotificationModel]:
    """获取通知列表

    Args:
        client: ApiClient 实例
        n: 获取通知数量，默认 60
        pf_kwargs: 分页查询相关参数

    Returns:
        通知列表的异步迭代器
    """
    api = NotificationsApi(client)

    @auto_parse_iterator_return(NotificationModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int):
        result = await cast(
            "Awaitable[list]",
            run_sync(api.get_notifications)(n=page_size, offset=offset),
        )
        return result or []

    return iterator()


async def get_notification(
    client: ApiClient,
    notification_id: str,
) -> NotificationModel:
    """获取指定通知详情

    Args:
        client: ApiClient 实例
        notification_id: 通知 ID

    Returns:
        通知详情
    """
    api = NotificationsApi(client)
    result = await cast(
        "Awaitable[Notification]",
        run_sync(api.get_notification)(notification_id=notification_id),
    )
    return NotificationModel(**result.to_dict())


async def accept_friend_request(
    client: ApiClient,
    notification_id: str,
) -> Success:
    """接受好友请求

    Args:
        client: ApiClient 实例
        notification_id: 通知 ID

    Returns:
        操作结果
    """
    api = NotificationsApi(client)
    return await cast(
        "Awaitable[Success]",
        run_sync(api.accept_friend_request)(notification_id=notification_id),
    )


async def mark_notification_as_read(
    client: ApiClient,
    notification_id: str,
) -> Success:
    """将通知标记为已读

    Args:
        client: ApiClient 实例
        notification_id: 通知 ID

    Returns:
        操作结果
    """
    api = NotificationsApi(client)
    return await cast(
        "Awaitable[Success]",
        run_sync(api.mark_notification_as_read)(notification_id=notification_id),
    )


async def delete_notification(
    client: ApiClient,
    notification_id: str,
) -> Success:
    """删除通知

    Args:
        client: ApiClient 实例
        notification_id: 通知 ID

    Returns:
        操作结果
    """
    api = NotificationsApi(client)
    return await cast(
        "Awaitable[Success]",
        run_sync(api.delete_notification)(notification_id=notification_id),
    )


async def clear_notifications(client: ApiClient) -> bool:
    """清除所有通知

    Args:
        client: ApiClient 实例

    Returns:
        是否清除成功
    """
    api = NotificationsApi(client)
    await run_sync(api.clear_notifications)()
    return True


# region Notification V2 APIs


def get_notification_v2s(
    client: ApiClient,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[NotificationModel]:
    """获取 V2 通知列表

    Args:
        client: ApiClient 实例
        pf_kwargs: 分页查询相关参数

    Returns:
        V2 通知列表的异步迭代器
    """
    api = NotificationsApi(client)

    @auto_parse_iterator_return(NotificationModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int):
        result = await cast(
            "Awaitable[list]",
            run_sync(api.get_notification_v2s)(n=page_size, offset=offset),
        )
        return result or []

    return iterator()


async def get_notification_v2(
    client: ApiClient,
    notification_id: str,
) -> NotificationModel:
    """获取 V2 通知详情

    Args:
        client: ApiClient 实例
        notification_id: 通知 ID

    Returns:
        V2 通知详情
    """
    api = NotificationsApi(client)
    result = await cast(
        "Awaitable[Notification]",
        run_sync(api.get_notification_v2)(notification_id=notification_id),
    )
    return NotificationModel(**result.to_dict())


async def acknowledge_notification_v2(
    client: ApiClient,
    notification_id: str,
) -> bool:
    """确认 V2 通知

    Args:
        client: ApiClient 实例
        notification_id: 通知 ID

    Returns:
        是否确认成功
    """
    api = NotificationsApi(client)
    await run_sync(api.acknowledge_notification_v2)(notification_id=notification_id)
    return True


async def delete_notification_v2(
    client: ApiClient,
    notification_id: str,
) -> Success:
    """删除 V2 通知

    Args:
        client: ApiClient 实例
        notification_id: 通知 ID

    Returns:
        操作结果
    """
    api = NotificationsApi(client)
    return await cast(
        "Awaitable[Success]",
        run_sync(api.delete_notification_v2)(notification_id=notification_id),
    )


async def delete_all_notification_v2s(client: ApiClient) -> bool:
    """删除所有 V2 通知

    Args:
        client: ApiClient 实例

    Returns:
        是否删除成功
    """
    api = NotificationsApi(client)
    await run_sync(api.delete_all_notification_v2s)()
    return True
