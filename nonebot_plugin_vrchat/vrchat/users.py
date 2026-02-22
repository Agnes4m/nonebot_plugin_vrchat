from collections.abc import AsyncIterable, Awaitable
from typing import TYPE_CHECKING, Optional, cast
from typing_extensions import Unpack

from nonebot.utils import run_sync
from vrchatapi import ApiClient, Group, UsersApi
from vrchatapi.models import Feedback, User

from .types import (
    GroupInstanceModel,
    GroupModel,
    LimitedGroupModel,
    LimitedUserModel,
    UserModel,
    UserNoteModel,
)
from .utils import (
    IterPFKwargs,
    auto_parse_iterator_return,
    auto_parse_return,
    iter_pagination_func,
    user_agent,
)

if TYPE_CHECKING:
    from vrchatapi.models import UserNote


def search_users(
    client: ApiClient,
    keyword: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[LimitedUserModel]:
    """
    搜索用户

    Args:
        client: ApiClient 实例
        keyword: 搜索关键词
        pf_kwargs: 分页查询相关参数

    Returns:
        获取搜索到用户的异步迭代器
    """
    client.user_agent = user_agent
    api = UsersApi(client)

    @auto_parse_iterator_return(LimitedUserModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int):
        result = await cast(
            "Awaitable[list]",
            run_sync(api.search_users)(search=keyword, n=page_size, offset=offset),
        )
        return result or []

    return iterator()


@auto_parse_return(UserModel)
async def get_user(client: ApiClient, user_id: str) -> User:
    """
    通过用户 ID 获取用户信息

    Args:
        client: ApiClient 实例
        user_id: 用户 ID

    Returns:
        用户信息
    """
    client.user_agent = user_agent
    api = UsersApi(client)
    return await cast(
        "Awaitable[User]",
        run_sync(api.get_user)(user_id=user_id),
    )


@auto_parse_return(UserModel)
async def get_user_by_name(client: ApiClient, username: str) -> User:
    """
    通过用户名获取用户信息

    Args:
        client: ApiClient 实例
        username: 用户名

    Returns:
        用户信息
    """
    client.user_agent = user_agent
    api = UsersApi(client)
    return await cast(
        "Awaitable[User]",
        run_sync(api.get_user_by_name)(username=username),
    )


@auto_parse_return(UserModel)
async def update_user(
    client: ApiClient,
    user_id: str,
    update_user_request: dict,
) -> User:
    """
    更新用户信息

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        update_user_request: 更新用户请求对象

    Returns:
        更新后的用户信息
    """
    from vrchatapi.models import UpdateUserRequest

    client.user_agent = user_agent
    api = UsersApi(client)
    return await cast(
        "Awaitable[User]",
        run_sync(api.update_user)(
            user_id=user_id,
            update_user_request=UpdateUserRequest(**update_user_request),
        ),
    )


async def add_tags(
    client: ApiClient,
    user_id: str,
    tags: list[str],
) -> bool:
    """
    添加用户标签

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        tags: 要添加的标签列表

    Returns:
        是否添加成功
    """
    from vrchatapi.models import ChangeUserTagsRequest

    client.user_agent = user_agent
    api = UsersApi(client)
    await run_sync(api.add_tags)(
        user_id=user_id,
        change_user_tags_request=ChangeUserTagsRequest(tags=tags),
    )
    return True


async def remove_tags(
    client: ApiClient,
    user_id: str,
    tags: list[str],
) -> bool:
    """
    移除用户标签

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        tags: 要移除的标签列表

    Returns:
        是否移除成功
    """
    from vrchatapi.models import ChangeUserTagsRequest

    client.user_agent = user_agent
    api = UsersApi(client)
    await run_sync(api.remove_tags)(
        user_id=user_id,
        change_user_tags_request=ChangeUserTagsRequest(tags=tags),
    )
    return True


async def get_user_note(
    client: ApiClient,
    note_user_id: str,
) -> UserNoteModel:
    """
    获取用户笔记

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        note_user_id: 笔记目标用户 ID

    Returns:
        用户笔记信息
    """

    client.user_agent = user_agent
    api = UsersApi(client)
    result = await cast(
        "Awaitable[UserNote]",
        run_sync(api.get_user_note)(
            user_note_id=note_user_id,
        ),
    )
    return UserNoteModel(**result.to_dict())


def get_user_notes(
    client: ApiClient,
    user_id: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[UserNoteModel]:
    """
    获取用户的所有笔记

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        pf_kwargs: 分页查询相关参数

    Returns:
        获取用户笔记的异步迭代器
    """
    client.user_agent = user_agent
    api = UsersApi(client)

    @auto_parse_iterator_return(UserNoteModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int):
        result = await cast(
            "Awaitable[list]",
            run_sync(api.get_user_notes)(
                user_id=user_id,
                n=page_size,
                offset=offset,
            ),
        )
        return result or []

    return iterator()


async def update_user_note(
    client: ApiClient,
    user_id: str,
    note_user_id: str,
    update_user_note_request: dict,
) -> UserNoteModel:
    """
    更新用户笔记

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        note_user_id: 笔记目标用户 ID
        update_user_note_request: 更新笔记请求对象

    Returns:
        更新后的用户笔记信息
    """
    from vrchatapi.models import UpdateUserNoteRequest

    client.user_agent = user_agent
    api = UsersApi(client)
    result = await cast(
        "Awaitable[UserNote]",
        run_sync(api.update_user_note)(
            user_id=user_id,
            noteUserId=note_user_id,
            update_user_note_request=UpdateUserNoteRequest(
                **update_user_note_request,
            ),
        ),
    )
    return UserNoteModel(**result.to_dict())


async def get_user_groups(
    client: ApiClient,
    user_id: str,
) -> list[GroupModel]:
    """
    获取用户加入的群组列表

    Args:
        client: ApiClient 实例
        user_id: 用户 ID

    Returns:
        群组列表
    """
    client.user_agent = user_agent
    api = UsersApi(client)
    groups = await cast(
        "Awaitable[list]",
        run_sync(api.get_user_groups)(user_id=user_id),
    )
    return [GroupModel(**g.to_dict()) for g in groups] if groups else []


async def get_user_group_requests(
    client: ApiClient,
    user_id: str,
) -> list[LimitedGroupModel]:
    """
    获取用户的群组请求列表

    Args:
        client: ApiClient 实例
        user_id: 用户 ID

    Returns:
        群组请求列表
    """
    client.user_agent = user_agent
    api = UsersApi(client)
    groups = await cast(
        "Awaitable[list]",
        run_sync(api.get_user_group_requests)(user_id=user_id),
    )
    return [LimitedGroupModel(**g.to_dict()) for g in groups] if groups else []


async def get_user_group_instances(
    client: ApiClient,
    user_id: str,
) -> list[GroupInstanceModel]:
    """
    获取用户的群组实例列表

    Args:
        client: ApiClient 实例
        user_id: 用户 ID

    Returns:
        群组实例列表
    """
    client.user_agent = user_agent
    api = UsersApi(client)
    instances = await cast(
        "Awaitable[list]",
        run_sync(api.get_user_group_instances)(user_id=user_id),
    )
    return [GroupInstanceModel(**i.to_dict()) for i in instances] if instances else []


async def get_user_group_instances_for_group(
    client: ApiClient,
    user_id: str,
    group_id: str,
) -> list[GroupInstanceModel]:
    """
    获取用户在指定群组的实例列表

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        group_id: 群组 ID

    Returns:
        群组实例列表
    """
    client.user_agent = user_agent
    api = UsersApi(client)
    instances = await cast(
        "Awaitable[list]",
        run_sync(api.get_user_group_instances_for_group)(
            user_id=user_id,
            group_id=group_id,
        ),
    )
    return [GroupInstanceModel(**i.to_dict()) for i in instances] if instances else []


async def get_user_all_group_permissions(
    client: ApiClient,
    user_id: str,
) -> list[GroupModel]:
    """
    获取用户在所有群组中的权限

    Args:
        client: ApiClient 实例
        user_id: 用户 ID

    Returns:
        群组权限列表
    """
    client.user_agent = user_agent
    api = UsersApi(client)
    groups = await cast(
        "Awaitable[list]",
        run_sync(api.get_user_all_group_permissions)(user_id=user_id),
    )
    return [GroupModel(**g.to_dict()) for g in groups] if groups else []


async def get_user_represented_group(
    client: ApiClient,
    user_id: str,
) -> Optional[GroupModel]:
    """
    获取用户代表的群组

    Args:
        client: ApiClient 实例
        user_id: 用户 ID

    Returns:
        群组信息
    """
    client.user_agent = user_agent
    api = UsersApi(client)
    group = await cast(
        "Awaitable[Group | None]",
        run_sync(api.get_user_represented_group)(user_id=user_id),
    )
    return GroupModel(**group.to_dict()) if group else None


async def get_mutuals(
    client: ApiClient,
    user_id: str,
) -> dict:
    """
    获取共同好友和群组信息

    Args:
        client: ApiClient 实例
        user_id: 用户 ID

    Returns:
        共同好友和群组信息
    """
    client.user_agent = user_agent
    api = UsersApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_mutuals)(user_id=user_id),
    )
    return result if isinstance(result, dict) else {}


def get_mutual_friends(
    client: ApiClient,
    user_id: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[LimitedUserModel]:
    """
    获取共同好友列表

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        pf_kwargs: 分页查询相关参数

    Returns:
        获取共同好友的异步迭代器
    """
    client.user_agent = user_agent
    api = UsersApi(client)

    @auto_parse_iterator_return(LimitedUserModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int):
        result = await cast(
            "Awaitable[list]",
            run_sync(api.get_mutual_friends)(
                user_id=user_id,
                n=page_size,
                offset=offset,
            ),
        )
        return result or []

    return iterator()


def get_mutual_groups(
    client: ApiClient,
    user_id: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[LimitedGroupModel]:
    """
    获取共同群组列表

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        pf_kwargs: 分页查询相关参数

    Returns:
        获取共同群组的异步迭代器
    """
    client.user_agent = user_agent
    api = UsersApi(client)

    @auto_parse_iterator_return(LimitedGroupModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int):
        result = await cast(
            "Awaitable[list]",
            run_sync(api.get_mutual_groups)(
                user_id=user_id,
                n=page_size,
                offset=offset,
            ),
        )
        return result or []

    return iterator()


def get_blocked_groups(
    client: ApiClient,
    user_id: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[LimitedGroupModel]:
    """
    获取用户屏蔽的群组列表

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        pf_kwargs: 分页查询相关参数

    Returns:
        获取屏蔽群组的异步迭代器
    """
    client.user_agent = user_agent
    api = UsersApi(client)

    @auto_parse_iterator_return(LimitedGroupModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int):
        result = await cast(
            "Awaitable[list]",
            run_sync(api.get_blocked_groups)(
                user_id=user_id,
                n=page_size,
                offset=offset,
            ),
        )
        return result or []

    return iterator()


def get_invited_groups(
    client: ApiClient,
    user_id: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[LimitedGroupModel]:
    """
    获取用户被邀请的群组列表

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        pf_kwargs: 分页查询相关参数

    Returns:
        获取被邀请群组的异步迭代器
    """
    client.user_agent = user_agent
    api = UsersApi(client)

    @auto_parse_iterator_return(LimitedGroupModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int):
        result = await cast(
            "Awaitable[list]",
            run_sync(api.get_invited_groups)(
                user_id=user_id,
                n=page_size,
                offset=offset,
            ),
        )
        return result or []

    return iterator()


def get_user_feedback(
    client: ApiClient,
    user_id: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[Feedback]:
    """
    获取用户反馈列表

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        pf_kwargs: 分页查询相关参数

    Returns:
        获取用户反馈的异步迭代器
    """
    client.user_agent = user_agent
    api = UsersApi(client)

    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int):
        result = await cast(
            "Awaitable[list]",
            run_sync(api.get_user_feedback)(
                user_id=user_id,
                n=page_size,
                offset=offset,
            ),
        )
        return result or []

    return iterator()


async def update_badge(
    client: ApiClient,
    user_id: str,
    badge_id: str,
    update_user_badge_request: dict,
) -> UserModel:
    """
    更新用户徽章

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        badge_id: 徽章 ID
        update_user_badge_request: 更新徽章请求对象

    Returns:
        更新后的用户信息
    """
    from vrchatapi.models import UpdateUserBadgeRequest

    client.user_agent = user_agent
    api = UsersApi(client)
    user = await cast(
        "Awaitable[User]",
        run_sync(api.update_badge)(
            user_id=user_id,
            badge_id=badge_id,
            update_user_badge_request=UpdateUserBadgeRequest(
                **update_user_badge_request,
            ),
        ),
    )
    return UserModel(**user.to_dict())
