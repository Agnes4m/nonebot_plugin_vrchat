from typing import AsyncIterator, Awaitable, List, Optional, cast

from nonebot.utils import run_sync
from vrchatapi import ApiClient, LimitedUser, User, UsersApi

from .types import LimitedUserModel, UserModel
from .utils import auto_parse_iterator_return, auto_parse_return, iter_pagination_func


# 定义一个搜索用户的函数，该函数使用给定的ApiClient实例，搜索关键字，分页大小和偏移量来搜索用户
def search_users(
    client: ApiClient,  # 传入ApiClient实例作为参数
    keyword: str,  # 传入搜索关键字
    page_size: int = 10,  # 定义分页大小，默认为10
    offset: int = 0,  # 定义偏移量，默认为0
) -> AsyncIterator[LimitedUserModel]:  # 函数返回一个异步迭代器，生成LimitedUserModel类型的对象
    # 创建一个UsersApi实例，使用传入的ApiClient实例
    api = UsersApi(client)

    # 使用装饰器auto_parse_iterator_return和iter_pagination_func定义iterator函数，该函数用于获取搜索结果的分页数据
    # page_size和offset作为参数传入iter_pagination_func装饰器，用于控制分页
    @auto_parse_iterator_return(LimitedUserModel)
    @iter_pagination_func(page_size=page_size, offset=offset)
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


# 下面的代码块对LimitedUser类进行一些修改，首先是增加openapi_types和attribute_map，然后修改__init__方法
# region monkey patch LimitedUser  # 第一部分：LimitedUser类的修改
# 在LimitedUser类中增加openapi_types字典，将"last_login"映射为"datetime"类型
LimitedUser.openapi_types["last_login"] = "datetime"
# 在LimitedUser类中增加attribute_map字典，将"last_login"映射为"last_login"属性名
LimitedUser.attribute_map["last_login"] = "last_login"

# 保存LimitedUser类的原始__init__方法
_original_limited_user_init = LimitedUser.__init__


# 定义一个新的__init__方法，首先尝试从关键字参数中获取"last_login"，如果找不到则设定为None
def patched_limited_user_init(self: LimitedUser, *args, **kwargs) -> None:
    try:
        self.last_login = kwargs.pop("last_login")  # type: ignore  # 从关键字参数中获取"last_login"的值并赋值给self.last_login
    except KeyError:
        LimitedUser.last_login = None  # type: ignore  # 如果找不到"last_login"关键字参数，则将LimitedUser类的last_login属性设为None
    # 调用原始的__init__方法，传递除"last_login"之外的所有参数
    _original_limited_user_init(self, *args, **kwargs)


# 将LimitedUser的__init__方法替换为上面定义的新方法
LimitedUser.__init__ = patched_limited_user_init  # type: ignore
# endregion  # 第一部分结束：LimitedUser类的修改


# region monkey patch User  # 第二部分：User类的修改
# 定义一个新的属性getter和setter方法，用于获取和设置User实例的instance_id属性值
def patched_instance_id_getter(self: User) -> Optional[str]:
    return self._instance_id  # 返回当前User实例的instance_id属性


def patched_instance_id_setter(self: User, value: str) -> None:
    self._instance_id = value  # 设置当前User实例的instance_id属性值为传入的值


setattr(  # noqa: B010
    User,
    "instance_id",
    property(patched_instance_id_getter, patched_instance_id_setter),
)
# endregion  # 第二部分结束：User类的修改
