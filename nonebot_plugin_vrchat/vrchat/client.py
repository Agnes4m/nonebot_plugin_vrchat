from http.cookiejar import LWPCookieJar
from pathlib import Path
from typing import Optional

from nonebot import logger
from nonebot.utils import run_sync
from pydantic import BaseModel
from vrchatapi import ApiClient, Configuration, NotificationsApi
from vrchatapi.exceptions import UnauthorizedException

from ..config import DATA_DIR
from .utils import user_agent

_c = Configuration()
_c.client_side_validation = False
Configuration.set_default(_c)

_last_usable_client: Optional[ApiClient] = None

PLAYER_PATH = DATA_DIR / "player"
PLAYER_PATH.mkdir(parents=True, exist_ok=True)


def _restrict_file_permissions(path: Path) -> None:
    """将敏感文件权限收紧为 0o600（仅所有者可读写）。"""
    try:
        path.chmod(0o600)
    except OSError:
        logger.warning(f"无法收紧文件权限: {path}")


class NotLoggedInError(Exception):
    pass


class LoginInfo(BaseModel):
    username: str
    password: str
    user_id: str = ""


def save_client_cookies(client: ApiClient, session_id: str):
    path = PLAYER_PATH / f"{session_id}.cookies"
    cookie_jar = LWPCookieJar(filename=path)
    for cookie in client.rest_client.cookie_jar:
        cookie_jar.set_cookie(cookie)
    cookie_jar.save()
    _restrict_file_permissions(path)


def load_cookies_to_client(client: ApiClient, session_id: str):
    path = PLAYER_PATH / f"{session_id}.cookies"
    if not path.exists():
        raise NotLoggedInError
    cookie_jar = LWPCookieJar(filename=path)
    cookie_jar.load()
    for cookie in cookie_jar:
        client.rest_client.cookie_jar.set_cookie(cookie)


def remove_cookies(session_id: str):
    path = PLAYER_PATH / f"{session_id}.cookies"
    if path.exists():
        path.unlink()


def get_login_info(session_id: str) -> LoginInfo:
    info_path = PLAYER_PATH / f"{session_id}.json"
    if not info_path.exists():
        raise NotLoggedInError
    return LoginInfo.model_validate_json(info_path.read_text(encoding="utf-8"))


def remove_login_info(session_id: str):
    info_path = PLAYER_PATH / f"{session_id}.json"
    if info_path.exists():
        info_path.unlink()
    remove_cookies(session_id)


def save_user_id(session_id: str, user_id: str):
    info_path = PLAYER_PATH / f"{session_id}.json"
    if info_path.exists():
        info = LoginInfo.model_validate_json(info_path.read_text(encoding="utf-8"))
        info.user_id = user_id
        write_login_info(
            session_id,
            username=info.username,
            password=info.password,
            user_id=info.user_id,
        )
    else:
        write_login_info(session_id, username="", password="", user_id=user_id)


def get_user_id(session_id: str) -> str:
    info_path = PLAYER_PATH / f"{session_id}.json"
    if not info_path.exists():
        return ""
    try:
        info = LoginInfo.model_validate_json(info_path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    return info.user_id


def write_login_info(
    session_id: str,
    username: str,
    password: str,
    user_id: str = "",
) -> None:
    """写入登录信息，并收紧文件权限。"""
    info_path = PLAYER_PATH / f"{session_id}.json"
    info_path.write_text(
        LoginInfo(
            username=username,
            password=password,
            user_id=user_id,
        ).model_dump_json(indent=2),
        encoding="utf-8",
    )
    _restrict_file_permissions(info_path)


async def get_client(
    session_id: str,
    login_info: Optional[LoginInfo] = None,
) -> ApiClient:
    load_cookies = not login_info
    login_info = login_info or get_login_info(session_id)
    configuration = Configuration(
        username=login_info.username,
        password=login_info.password,
    )
    configuration.client_side_validation = False
    client = ApiClient(configuration)
    client.user_agent = user_agent
    if load_cookies:
        load_cookies_to_client(client, session_id)
    return client


async def check_client_usable(client: ApiClient) -> bool:
    api = NotificationsApi(client)
    try:
        await run_sync(api.get_notifications)(n=1)
    except UnauthorizedException:
        return False
    return True


async def random_client() -> ApiClient:
    global _last_usable_client
    if _last_usable_client and (await check_client_usable(_last_usable_client)):
        return _last_usable_client
    for path in PLAYER_PATH.glob("*.cookies"):
        session_id = path.stem
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


async def get_or_random_client(session_id: str) -> tuple[ApiClient, bool]:
    try:
        return await get_client(session_id), True
    except NotLoggedInError:
        return await random_client(), False
