import asyncio
from collections.abc import AsyncIterable, Awaitable
from datetime import datetime
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Protocol,
    TypedDict,
    TypeVar,
)
from typing_extensions import NotRequired, ParamSpec, Unpack

from pydantic import BaseModel

T = TypeVar("T")
TM = TypeVar("TM", bound=BaseModel)
P = ParamSpec("P")
user_agent = "nonebot_plugin_vrchat/0.2.0 Z735803792@163.com"

DeveloperType = Literal["none", "trusted", "internal", "moderator"]
StatusType = Literal["active", "join me", "ask me", "busy", "offline"]
NormalizedStatusType = Literal[
    "online",
    "webonline",
    "joinme",
    "busy",
    "askme",
    "offline",
    "unknown",
]
TrustType = Literal[
    "visitor",
    "new",
    "user",
    "known",
    "trusted",
    "friend",
    "developer",
    "moderator",
]

NORMALIZE_STATUS_MAP: Dict[StatusType, NormalizedStatusType] = {
    "active": "online",
    "join me": "joinme",
    "busy": "busy",
    "ask me": "askme",
}
NORMALIZE_TRUST_TAG_MAP: Dict[str, TrustType] = {
    "veteran": "trusted",
    "trusted": "known",
    "known": "user",
}
DEVELOPER_TRUST_TYPE_MAP: Dict[str, TrustType] = {
    "internal": "developer",
    "moderator": "moderator",
}
TRUST_TAG_PREFIX = "system_trust_"


def normalize_status(
    status: StatusType,
    location: Optional[str],
) -> NormalizedStatusType:
    if location == "offline":
        return "webonline" if status == "active" else "offline"
    return NORMALIZE_STATUS_MAP.get(status, "unknown")


def extract_trust_level(tags: List[str], developer_type: Optional[str]) -> TrustType:
    if developer_type in DEVELOPER_TRUST_TYPE_MAP:
        return DEVELOPER_TRUST_TYPE_MAP[developer_type]
    for suffix in NORMALIZE_TRUST_TAG_MAP:
        if f"{TRUST_TAG_PREFIX}{suffix}" in tags:
            return NORMALIZE_TRUST_TAG_MAP[suffix]
    return "visitor"


def format_datetime(dt: datetime | str | None) -> str:
    if not dt:
        return "未知"
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)


class HasToDictProtocol(Protocol):
    def to_dict(self) -> dict: ...


class PaginationCallable(Protocol, Generic[T]):
    async def __call__(self, page_size: int, offset: int) -> Optional[list[T]]: ...


class ApiModelClass(Protocol):
    openapi_types: dict[str, str]
    attribute_map: dict[str, str]
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

    def decorator(func: PaginationCallable[T]) -> Callable[[], AsyncIterable[T]]:
        @wraps(func)
        async def wrapper():
            now_offset = offset
            while True:
                if has_max_size and now_offset >= max_size:
                    break
                now_page_size = (
                    min(page_size, max_size - now_offset) if has_max_size else page_size
                )
                resp = await func(now_page_size, now_offset)
                if not resp:
                    break
                for x in resp:
                    yield x
                now_offset += page_size
                if delay:
                    await asyncio.sleep(delay)

        return wrapper

    return decorator


def auto_parse_iterator_return(model: type[TM]):
    def decorator(
        func: Callable[P, AsyncIterable[HasToDictProtocol]],
    ) -> Callable[P, AsyncIterable[TM]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs):
            async for x in func(*args, **kwargs):
                yield model(**x.to_dict())

        return wrapper

    return decorator


def auto_parse_return(model: type[TM]):
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
    cls: type[TModelClass],
    attr: str,
    real_attr: str,
    attr_type: str,
    default: Optional[Any] = None,
):
    if attr in cls.openapi_types or attr in cls.attribute_map:
        return
    cls.openapi_types[attr] = attr_type
    cls.attribute_map[attr] = real_attr
    original_init = cls.__init__

    @wraps(original_init)
    def patched_init(self: TModelClass, *args, **kwargs) -> None:
        setattr(self, attr, kwargs.pop(attr, default))
        original_init(self, *args, **kwargs)

    cls.__init__ = patched_init
