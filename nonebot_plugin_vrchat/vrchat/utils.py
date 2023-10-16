import asyncio
from functools import wraps
from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    Type,
    TypedDict,
    TypeVar,
)
from typing_extensions import NotRequired, ParamSpec, Unpack

from pydantic import BaseModel

T = TypeVar("T")
TM = TypeVar("TM", bound=BaseModel)
P = ParamSpec("P")


class HasToDictProtocol(Protocol):
    def to_dict(self) -> dict:
        ...


class PaginationCallable(Protocol, Generic[T]):
    async def __call__(self, page_size: int, offset: int) -> Optional[List[T]]:
        ...


class ApiModelClass(Protocol):
    """代表 `vrchatapi` 中调用 API 返回的数据结构"""

    openapi_types: Dict[str, str]
    attribute_map: Dict[str, str]
    __init__: Callable[..., None]


class IterPFKwargs(TypedDict):
    """分页查询相关参数"""

    page_size: NotRequired[int]
    """单次查询的数量，默认为 `100`"""
    offset: NotRequired[int]
    """查询的初始偏移量，默认为 `0`"""
    delay: NotRequired[float]
    """每次查询后的延迟时间，单位秒，默认为 `0`"""
    max_size: NotRequired[int]
    """最大结果数，返回的结果数永远不会超过这个值，默认为 `0`，即不限制"""


TModelClass = TypeVar("TModelClass", bound=ApiModelClass)


def iter_pagination_func(**kwargs: Unpack[IterPFKwargs]):
    """
    用于装饰 `PaginationCallable` 的装饰器，使其变成一个 `Callable[[], AsyncIterable[T]]`

    Args:
        见 `IterPFKwargs`
    """

    # 从 kwargs 中获取相关参数
    page_size = kwargs.get("page_size", 100)
    offset = kwargs.get("offset", 0)
    delay = kwargs.get("delay", 0.0)
    max_size = kwargs.get("max_size", 0)
    has_max_size = max_size > 0

    def decorator(func: PaginationCallable[T]) -> Callable[[], AsyncIterable[T]]:
        @wraps(func)
        async def wrapper():
            now_offset = offset
            while True:
                # 如果声明了最大结果数，
                # 那么确保 本次查询的数量 不会超过 剩余的最大结果数
                now_page_size = (
                    min(page_size, max_size - now_offset) if has_max_size else page_size
                )

                resp = await func(now_page_size, now_offset)
                if not resp:
                    break  # 本页无结果，结束迭代

                for x in resp:
                    yield x  # 将返回列表中的结果逐个返回

                now_offset += page_size
                if max_size > 0 and now_offset >= max_size:
                    break  # 达到最大结果数，结束迭代

                if delay:
                    await asyncio.sleep(delay)

        return wrapper

    return decorator


def auto_parse_iterator_return(model: Type[TM]):
    """
    用于装饰返回 `HasToDictProtocol` 异步迭代器的函数，
    对此函数返回的迭代器每次迭代返回的值调用 `.to_dict()` 后使用指定的 `BaseModel` 解析并返回

    Args:
        model: 要解析为的 `BaseModel` 类型
    """

    def decorator(
        func: Callable[P, AsyncIterable[HasToDictProtocol]],
    ) -> Callable[P, AsyncIterable[TM]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs):
            async for x in func(*args, **kwargs):
                yield model(**x.to_dict())

        return wrapper

    return decorator


def auto_parse_return(model: Type[TM]):
    """
    用于装饰返回 `HasToDictProtocol` 的异步函数，
    对此函数返回的值调用 `.to_dict()` 后使用指定的 `BaseModel` 解析并返回

    Args:
        model: 要解析为的 `BaseModel` 类型
    """

    def decorator(
        func: Callable[P, Awaitable[HasToDictProtocol]],
    ) -> Callable[P, Awaitable[TM]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs):
            resp = await func(*args, **kwargs)
            return model(**resp.to_dict())

        return wrapper

    return decorator


def patch_api_model_append_attr(
    cls: Type[TModelClass],
    attr: str,
    real_attr: str,
    attr_type: str,
    default: Optional[Any] = None,
):
    """
    向属于 `ApiModelClass` 的类型中添加一个新属性（Monkey Patch）

    Args:
        cls: 要添加属性到的类
        attr: 要添加的属性名
        real_attr: 要添加的属性名对应的 API 返回值的键名
        attr_type: 该属性对应的返回类型
        default: 该属性的默认值
    """

    if hasattr(cls, attr):
        raise ValueError(f"Attribute `{attr}` already exists")

    cls.openapi_types[attr] = attr_type
    cls.attribute_map[attr] = real_attr

    original_init = cls.__init__

    @wraps(original_init)
    def patched_init(self: TModelClass, *args, **kwargs) -> None:
        setattr(self, attr, kwargs.pop(attr, default))
        original_init(self, *args, **kwargs)

    cls.__init__ = patched_init
