from http.cookiejar import LWPCookieJar
from typing import Optional

from async_lru import alru_cache
from nonebot import logger
from nonebot.adapters.qqguild.exception import UnauthorizedException
from nonebot.utils import run_sync
from pydantic import BaseModel
from vrchatapi import ApiClient, Configuration, NotificationsApi

from ..config import config

# disable client side validation
_c = Configuration()
_c.client_side_validation = False
Configuration.set_default(_c)


_last_usable_client: Optional[ApiClient] = None


PLAYER_PATH = config.vrc_path / "player"
PLAYER_PATH.mkdir(parents=True, exist_ok=True)


class NotLoggedInError(Exception):
    pass


class LoginInfo(BaseModel):
    username: str
    password: str


def save_client_cookies(client: ApiClient, session_id: str):
    path = PLAYER_PATH / f"{session_id}.cookies"

    cookie_jar = LWPCookieJar(filename=path)
    for cookie in client.rest_client.cookie_jar:
        cookie_jar.set_cookie(cookie)

    cookie_jar.save()


def load_cookies_to_client(client: ApiClient, session_id: str):
    path = PLAYER_PATH / f"{session_id}.cookies"
    if not path.exists():
        return

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
    cookie_path = PLAYER_PATH / f"{session_id}.cookies"
    if not (info_path.exists() and cookie_path.exists()):
        raise NotLoggedInError
    return LoginInfo.parse_raw(info_path.read_text(encoding="utf-8"))


def remove_login_info(session_id: str):
    info_path = PLAYER_PATH / f"{session_id}.json"
    if info_path.exists():
        info_path.unlink()
    remove_cookies(session_id)


async def get_client(
    session_id: str,
    login_info: Optional[LoginInfo] = None,
) -> ApiClient:
    login_info = login_info or get_login_info(session_id)
    configuration = Configuration(
        username=login_info.username,
        password=login_info.password,
    )
    configuration.client_side_validation = False
    client = ApiClient(configuration)
    load_cookies_to_client(client, session_id)
    return client


@alru_cache(ttl=10)
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

    raise NotLoggedInError


async def get_or_random_client(session_id: str) -> ApiClient:
    try:
        return await get_client(session_id)
    except NotLoggedInError:
        return await random_client()
