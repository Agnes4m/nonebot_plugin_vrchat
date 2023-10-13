from typing import AsyncIterator, Awaitable, List, Optional, cast

from nonebot.utils import run_sync
from vrchatapi import ApiClient, LimitedUser, User, UsersApi

from .types import LimitedUserModel, UserModel
from .utils import auto_parse_iterator_return, auto_parse_return, iter_pagination_func


def search_users(
    client: ApiClient,
    keyword: str,
    page_size: int = 10,
    offset: int = 0,
) -> AsyncIterator[LimitedUserModel]:
    api = UsersApi(client)

    @auto_parse_iterator_return(LimitedUserModel)
    @iter_pagination_func(page_size=page_size, offset=offset)
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


# region monkey patch LimitedUser
LimitedUser.openapi_types["last_login"] = "datetime"
LimitedUser.attribute_map["last_login"] = "last_login"

_original_limited_user_init = LimitedUser.__init__


def patched_limited_user_init(self: LimitedUser, *args, **kwargs) -> None:
    try:
        self.last_login = kwargs.pop("last_login")  # type: ignore
    except KeyError:
        LimitedUser.last_login = None  # type: ignore
    _original_limited_user_init(self, *args, **kwargs)


LimitedUser.__init__ = patched_limited_user_init  # type: ignore
# endregion


# region monkey patch User
def patched_instance_id_getter(self: User) -> Optional[str]:
    return self._instance_id


def patched_instance_id_setter(self: User, value: str) -> None:
    self._instance_id = value


setattr(  # noqa: B010
    User,
    "instance_id",
    property(patched_instance_id_getter, patched_instance_id_setter),
)
# endregion
