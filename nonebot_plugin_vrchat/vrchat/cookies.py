"""
Uitl functions to manage cookies of VRChat API.
"""

from http.cookiejar import LWPCookieJar

# from pathlib import Path
import vrchatapi

from ..config import config


def save_cookies(client: vrchatapi.ApiClient, filename: str = "./cookies.txt"):
    """Save current session cookies

    Args:
        filename (str): Path to save cookies to
    """

    cookie_jar = LWPCookieJar(filename=filename)

    for cookie in client.rest_client.cookie_jar:
        cookie_jar.set_cookie(cookie)

    cookie_jar.save()


def load_cookies(client: vrchatapi.ApiClient, filename: str = "./cookies.txt"):
    """Load cached session cookies from file

    Args:
        filename (str): Path to load cookies from
    """

    cookie_jar = LWPCookieJar(filename=filename)

    try:
        cookie_jar.load()
    except FileNotFoundError:
        cookie_jar.save()
        return

    for cookie in cookie_jar:
        client.rest_client.cookie_jar.set_cookie(cookie)


def remove_cookies(filename: str = "cookies"):
    """
    remove cookies file
    """
    if config.vrc_path.joinpath(filename).exists:
        config.vrc_path.joinpath(filename).unlink()
