from typing import NoReturn

from nonebot.log import logger
from nonebot.matcher import Matcher

from .message import ErrorMsg
from .vrchat import ApiException, NotLoggedInError, UnauthorizedException


async def handle_error(matcher: Matcher, e: Exception) -> NoReturn:
    if isinstance(e, NotLoggedInError):
        await matcher.finish(ErrorMsg.Log)

    if isinstance(e, UnauthorizedException):
        logger.warning(f"UnauthorizedException: {e}")
        await matcher.finish(ErrorMsg.Unauth)

    if isinstance(e, ApiException):
        logger.error(f"Error when requesting api: [{e.status}] {e.reason}")
        await matcher.finish(f"服务器返回异常：[{e.status}] {e.reason}")

    logger.exception("Exception when requesting api")
    await matcher.finish(ErrorMsg.Unkown)
