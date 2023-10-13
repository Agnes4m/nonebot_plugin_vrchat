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
    TypeVar,
)
from typing_extensions import ParamSpec

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


TModelClass = TypeVar("TModelClass", bound=ApiModelClass)


def iter_pagination_func(page_size: int = 100, offset: int = 0, delay: float = 0):
    def decorator(func: PaginationCallable[T]) -> Callable[[], AsyncIterator[T]]:
        async def wrapper():
            now_offset = offset
            while True:
                resp = await func(page_size, now_offset)
                if not resp:
                    break

                for x in resp:
                    yield x

                now_offset += page_size
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
