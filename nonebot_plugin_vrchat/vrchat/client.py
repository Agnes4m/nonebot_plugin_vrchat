import random
from http.cookiejar import LWPCookieJar
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from vrchatapi import ApiClient, Configuration

from ..config import config

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


def get_random_cookie() -> Optional[Path]:
    cookies = list(PLAYER_PATH.glob("*.cookies"))
    if cookies:
        return random.choice(cookies)
    return None


def get_client(session_id: str, login_info: Optional[LoginInfo] = None) -> ApiClient:
    login_info = login_info or get_login_info(session_id)
    configuration = Configuration(
        username=login_info.username,
        password=login_info.password,
    )
    client = ApiClient(configuration)
    load_cookies_to_client(client, session_id)
    return client


def random_client() -> ApiClient:
    cookie_path = get_random_cookie()
    if not cookie_path:
        raise NotLoggedInError
    return get_client(cookie_path.stem)


def get_or_random_client(session_id: str) -> ApiClient:
    try:
        return get_client(session_id)
    except NotLoggedInError:
        return random_client()
