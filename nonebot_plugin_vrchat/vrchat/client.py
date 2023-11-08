from http.cookiejar import LWPCookieJar
from typing import Optional

from nonebot import logger
from nonebot.utils import run_sync
from pydantic import BaseModel
from vrchatapi import ApiClient, Configuration, NotificationsApi
from vrchatapi.exceptions import UnauthorizedException

from ..config import DATA_DIR

# 关闭 `vrchatapi` 的客户端侧数据校验，这部分交给 pydantic 就行了
_c = Configuration()
_c.client_side_validation = False
Configuration.set_default(_c)


_last_usable_client: Optional[ApiClient] = None


# 用户登录信息文件夹
PLAYER_PATH = DATA_DIR / "player"
PLAYER_PATH.mkdir(parents=True, exist_ok=True)


class NotLoggedInError(Exception):
    """未登录错误，在未找到登录信息或 Cookies 时抛出"""


class LoginInfo(BaseModel):
    """用户登录信息"""

    username: str
    password: str


def save_client_cookies(client: ApiClient, session_id: str):
    """
    保存 ApiClient 的 Cookies 到文件

    Args:
        client: ApiClient 实例
        session_id: 用户 SessionID
    """

    path = PLAYER_PATH / f"{session_id}.cookies"

    cookie_jar = LWPCookieJar(filename=path)
    for cookie in client.rest_client.cookie_jar:
        cookie_jar.set_cookie(cookie)

    cookie_jar.save()


def load_cookies_to_client(client: ApiClient, session_id: str):
    """
    从文件加载用户 Cookies 到 ApiClient

    Args:
        client: ApiClient 实例
        session_id: 用户 SessionID

    Raises:
        NotLoggedInError: 用户 Cookies 不存在
    """

    path = PLAYER_PATH / f"{session_id}.cookies"
    if not path.exists():
        raise NotLoggedInError

    cookie_jar = LWPCookieJar(filename=path)
    cookie_jar.load()

    for cookie in cookie_jar:
        client.rest_client.cookie_jar.set_cookie(cookie)


def remove_cookies(session_id: str):
    """
    删除已保存的用户 Cookies 信息

    Args:
        session_id: 用户 SessionID
    """

    path = PLAYER_PATH / f"{session_id}.cookies"
    if path.exists():
        path.unlink()


def get_login_info(session_id: str) -> LoginInfo:
    """
    获取用户登录信息

    Args:
        session_id: 用户 SessionID

    Raises:
        NotLoggedInError: 用户信息不存在

    Returns:
        用户登录信息
    """

    info_path = PLAYER_PATH / f"{session_id}.json"
    if not info_path.exists():
        raise NotLoggedInError
    return LoginInfo.parse_raw(info_path.read_text(encoding="utf-8"))


def remove_login_info(session_id: str):
    """
    删除已保存的用户登录信息

    Args:
        session_id: 用户 SessionID

    Returns:
        用户登录信息
    """

    info_path = PLAYER_PATH / f"{session_id}.json"
    if info_path.exists():
        info_path.unlink()
    remove_cookies(session_id)


async def get_client(
    session_id: str,
    login_info: Optional[LoginInfo] = None,
) -> ApiClient:
    """
    通过用户 SessionID 获取已加载 Cookies 的 ApiClient 实例，
    或通过登录信息获取一个新的 ApiClient 实例

    Args:
        session_id: 用户 SessionID
        login_info: 登录信息

    Returns:
        ApiClient 实例
    """

    load_cookies = not login_info
    login_info = login_info or get_login_info(session_id)

    configuration = Configuration(
        username=login_info.username,
        password=login_info.password,
    )
    configuration.client_side_validation = False
    client = ApiClient(configuration)

    if load_cookies:
        load_cookies_to_client(client, session_id)

    return client


async def check_client_usable(client: ApiClient) -> bool:
    """
    检测 ApiClient 是否可用

    Args:
        client: ApiClient 实例

    Returns:
        ApiClient 是否可用
    """

    api = NotificationsApi(client)
    try:
        await run_sync(api.get_notifications)(n=1)
    except UnauthorizedException:  # 权限不足，未登录
        return False
    return True


async def random_client() -> ApiClient:
    """
    随机获取一个可用的 ApiClient 实例

    Raises:
        NotLoggedInError: 没有可用的 Cookies 信息

    Returns:
        ApiClient 实例
    """

    global _last_usable_client

    if _last_usable_client and (await check_client_usable(_last_usable_client)):
        return _last_usable_client

    # 遍历登录数据目录下所有用户 Cookies 文件
    for path in PLAYER_PATH.glob("*.cookies"):
        session_id = path.stem  # 获取不包含扩展名的文件名（即 SessionID）
        try:
            client = await get_client(session_id)
            if await check_client_usable(client):
                _last_usable_client = client
                return client

        except NotLoggedInError:
            logger.warning(f"Found cookies but has no login info: {session_id}")
        except Exception:
            logger.exception(f"Error when checking client usability: {session_id}")
        path.unlink()

    raise NotLoggedInError


async def get_or_random_client(session_id: str) -> ApiClient:
    """
    通过用户 SessionID 获取已加载 Cookies 的 ApiClient 实例，
    当不存在此用户的登录信息与 Cookies 时，返回一个可用的随机 ApiClient 实例

    Args:
        session_id: 用户 SessionID

    Raises:
        NotLoggedInError: 没有可用的 Cookies 信息

    Returns:
        ApiClient 实例
    """

    try:
        return await get_client(session_id)
    except NotLoggedInError:
        return await random_client()
