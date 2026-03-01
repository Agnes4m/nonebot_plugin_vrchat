from http.cookiejar import LWPCookieJar
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
        info_path.write_text(info.model_dump_json(indent=2), encoding="utf-8")
    else:
        info = LoginInfo(username="", password="", user_id=user_id)
        info_path.write_text(info.model_dump_json(indent=2), encoding="utf-8")


def get_user_id(session_id: str) -> str:
    info_path = PLAYER_PATH / f"{session_id}.json"
    if not info_path.exists():
        return ""
    try:
        info = LoginInfo.model_validate_json(info_path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    return info.user_id


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
