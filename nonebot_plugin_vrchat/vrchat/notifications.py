from typing import Awaitable, List, cast

from nonebot.utils import run_sync
from vrchatapi import ApiClient, NotificationsApi, Success
from vrchatapi.models import Notification


async def get_notifications(
    client: ApiClient,
    n: int = 60,
):
    """列表通知"""

    api = NotificationsApi(client)
    return await cast(
        Awaitable[List[Notification]],
        run_sync(api.get_notifications)(n=n),
    )


async def get_notification(
    client: ApiClient,
    notification_id: str,
):
    """显示通知"""

    api = NotificationsApi(client)
    return await cast(
        Awaitable[Notification],
        run_sync(api.get_notification)(notification_id=notification_id),
    )


async def accept_friend_request(
    client: ApiClient,
    notification_id: str,
):
    """接受好友请求"""

    api = NotificationsApi(client)
    return await cast(
        Awaitable[Success],
        run_sync(api.accept_friend_request)(notification_id=notification_id),
    )


async def mark_notification_as_read(
    client: ApiClient,
    notification_id: str,
):
    """将通知标记为已读"""

    api = NotificationsApi(client)
    return await cast(
        Awaitable[Success],
        run_sync(api.mark_notification_as_read)(notification_id=notification_id),
    )
