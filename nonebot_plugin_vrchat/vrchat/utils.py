import asyncio
from typing import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Generic,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
)

from pydantic import BaseModel
from typing_extensions import ParamSpec

# TypeVar用于类型变量，可以表示任意类型，T表示一个未知的类型
T = TypeVar("T")

# TypeVar用于类型变量，表示一个BaseModel的子类型，TM表示一个模型类型
TM = TypeVar("TM", bound=BaseModel)

# ParamSpec用于定义函数参数的类型规范，P表示一个参数
P = ParamSpec("P")


# 定义一个协议，该协议有一个to_dict方法，返回类型为dict
class HasToDictProtocol(Protocol):
    def to_dict(self) -> dict:
        ...


# 定义一个泛型协议，该协议有一个__call__方法，接受两个参数（page_size和offset），返回类型为Optional[List[T]]
class PaginationCallable(Protocol, Generic[T]):
    async def __call__(self, page_size: int, offset: int) -> Optional[List[T]]:
        ...


# 定义一个函数，这个函数接受三个参数（page_size，offset和delay），返回一个装饰器
def iter_pagination_func(page_size: int = 100, offset: int = 0, delay: float = 0):
    # 定义一个装饰器，接受一个具有PaginationCallable[T]类型的函数作为参数，返回一个无参数的异步生成器函数
    def decorator(func: PaginationCallable[T]) -> Callable[[], AsyncIterator[T]]:
        # 定义一个内部函数，该函数是一个异步生成器
        async def wrapper():
            # 初始化offset为传入的offset
            now_offset = offset
            # 当true为真时执行下面的循环
            while True:
                # 调用func方法并将返回的结果赋值给resp
                resp = await func(page_size, now_offset)
                # 如果resp为空则跳出循环
                if not resp:
                    break
                # 对resp中的每个元素执行下面的循环
                for x in resp:
                    # 生成一个元素并赋值给x
                    yield x
                # 将now_offset增加page_size
                now_offset += page_size
                # 如果delay不为0，则暂停delay秒
                if delay:
                    await asyncio.sleep(delay)

        # 返回wrapper函数
        return wrapper

    # 返回decorator函数
    return decorator


# 定义一个函数，这个函数接受一个模型类型（model）作为参数，返回一个装饰器
def auto_parse_iterator_return(model: Type[TM]):
    # 定义一个装饰器，接受一个具有Callable[P, AsyncIterable[HasToDictProtocol]]类型的函数作为参数，返回一个无参数的异步生成器函数
    def decorator(
        func: Callable[P, AsyncIterable[HasToDictProtocol]],
    ) -> Callable[P, AsyncIterator[TM]]:
        # 定义一个内部函数，该函数是一个异步生成器
        async def wrapper(*args: P.args, **kwargs: P.kwargs):
            # 对func的返回结果进行迭代并将结果赋值给x
            async for x in func(*args, **kwargs):
                # 将x转换为字典并使用model构造函数生成模型实例并赋值给x'
                yield model(**x.to_dict())

        # 返回wrapper函数
        return wrapper

    # 返回decorator函数
    return decorator


# 定义一个函数，这个函数接受一个模型类型（model）作为参数，返回一个装饰器
def auto_parse_return(model: Type[TM]):
    # 定义一个装饰器，接受一个具有Callable[P, Awaitable[HasToDictProtocol]]类型的函数作为参数，返回一个无参数的异步函数
    def decorator(
        func: Callable[P, Awaitable[HasToDictProtocol]],
    ) -> Callable[P, Awaitable[TM]]:
        # 定义一个内部函数，该函数是一个异步函数
        async def wrapper(*args: P.args, **kwargs: P.kwargs):
            # 等待func的返回结果并赋值给resp
            resp = await func(*args, **kwargs)
            # 将resp转换为字典并使用model构造函数生成模型实例并赋值给return_value
            return model(**resp.to_dict())

        # 返回wrapper函数
        return wrapper

    return decorator
