from typing import AsyncIterator, Awaitable, List, cast
from typing_extensions import Unpack

from nonebot.utils import run_sync
from vrchatapi import ApiClient, LimitedUser, User, UsersApi

from .types import LimitedUserModel, UserModel
from .utils import (
    IterPFKwargs,
    auto_parse_iterator_return,
    auto_parse_return,
    iter_pagination_func,
)


def search_users(
    client: ApiClient,
    keyword: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterator[LimitedUserModel]:
    api = UsersApi(client)

    @auto_parse_iterator_return(LimitedUserModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int) -> List[LimitedUser]:
        return await cast(
            Awaitable[List[LimitedUser]],
            run_sync(api.search_users)(search=keyword, n=page_size, offset=offset),
        )

    return iterator()


@auto_parse_return(UserModel)
async def get_user(client: ApiClient, user_id: str) -> User:
    api = UsersApi(client)
    return await cast(
        Awaitable[User],
        run_sync(api.get_user)(user_id=user_id),
    )
