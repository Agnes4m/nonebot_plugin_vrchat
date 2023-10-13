import asyncio
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
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
    openapi_types: Dict[str, str]
    attribute_map: Dict[str, str]
    __init__: Callable[..., None]


class IterPFKwargs(TypedDict):
    page_size: NotRequired[int]
    offset: NotRequired[int]
    delay: NotRequired[float]
    max_size: NotRequired[int]


TModelClass = TypeVar("TModelClass", bound=ApiModelClass)


def iter_pagination_func(**kwargs: Unpack[IterPFKwargs]):
    page_size = kwargs.get("page_size", 100)
    offset = kwargs.get("offset", 0)
    delay = kwargs.get("delay", 0.0)
    max_size = kwargs.get("max_size", 0)

    has_max_size = max_size > 0
    if has_max_size:
        page_size = min(page_size, max_size)

    def decorator(func: PaginationCallable[T]) -> Callable[[], AsyncIterator[T]]:
        async def wrapper():
            now_offset = offset
            while True:
                now_page_size = (
                    min(page_size, max_size - now_offset) if has_max_size else page_size
                )
                resp = await func(now_page_size, now_offset)
                if not resp:
                    break

                for x in resp:
                    yield x

                now_offset += page_size
                if max_size > 0 and now_offset >= max_size:
                    break

                if delay:
                    await asyncio.sleep(delay)

        return wrapper

    return decorator


def auto_parse_iterator_return(model: Type[TM]):
    def decorator(
        func: Callable[P, AsyncIterable[HasToDictProtocol]],
    ) -> Callable[P, AsyncIterator[TM]]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs):
            async for x in func(*args, **kwargs):
                yield model(**x.to_dict())

        return wrapper

    return decorator


def auto_parse_return(model: Type[TM]):
    def decorator(
        func: Callable[P, Awaitable[HasToDictProtocol]],
    ) -> Callable[P, Awaitable[TM]]:
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
    cls.openapi_types[attr] = attr_type
    cls.attribute_map[attr] = real_attr

    original_init = cls.__init__

    def patched_init(self: TModelClass, *args, **kwargs) -> None:
        setattr(self, attr, kwargs.pop(attr, default))
        original_init(self, *args, **kwargs)

    cls.__init__ = patched_init
