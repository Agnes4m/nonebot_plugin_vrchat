from typing import AsyncIterator, Awaitable, List, cast

from nonebot.utils import run_sync
from typing_extensions import Unpack
from vrchatapi import ApiClient, LimitedUser, User, UsersApi

from .types import LimitedUserModel, UserModel
from .utils import (
    IterPFKwargs,
    auto_parse_iterator_return,
    auto_parse_return,
    iter_pagination_func,
)


# 定义一个搜索用户的函数，该函数使用给定的ApiClient实例，搜索关键字，分页大小和偏移量来搜索用户
def search_users(
    client: ApiClient,
    keyword: str,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterator[LimitedUserModel]:
    api = UsersApi(client)

    # 使用装饰器auto_parse_iterator_return和iter_pagination_func定义iterator函数，该函数用于获取搜索结果的分页数据
    # page_size和offset作为参数传入iter_pagination_func装饰器，用于控制分页
    @auto_parse_iterator_return(LimitedUserModel)
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page_size: int, offset: int) -> List[LimitedUser]:
        # 调用api.search_users方法，传入搜索关键字、分页大小和偏移量，获取搜索结果，并转换为列表形式
        return await cast(
            Awaitable[List[LimitedUser]],
            run_sync(api.search_users)(search=keyword, n=page_size, offset=offset),
        )

    # 调用定义的iterator函数，并返回结果
    return iterator()


# 使用装饰器auto_parse_return定义get_user函数，该函数用于获取UserModel实例
@auto_parse_return(UserModel)
async def get_user(client: ApiClient, user_id: str) -> User:
    # 创建一个UsersApi实例，使用传入的ApiClient实例
    api = UsersApi(client)
    # 调用api.get_user方法，传入用户ID，获取用户信息，并转换为User实例
    return await cast(
        Awaitable[User],
        run_sync(api.get_user)(user_id=user_id),
    )
