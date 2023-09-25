"""
Uitl functions to manage cookies of VRChat API.
"""

from http.cookiejar import LWPCookieJar
from pathlib import Path


def save_cookies(client, filename: str = "cookies"):
    """Save current session cookies

    Args:
        filename (str): Path to save cookies to
    """

    cookie_jar = LWPCookieJar(filename=filename)

    for cookie in client.rest_client.cookie_jar:
        cookie_jar.set_cookie(cookie)

    cookie_jar.save("cookies")


def load_cookies(client, filename: Path = "cookies"):
    """Load cached session cookies from file

    Args:
        filename (str): Path to load cookies from
    """
    if Path(filename).exists:
        return
    cookie_jar = LWPCookieJar(filename=filename)
    try:
        cookie_jar.load("cookies")
    except FileNotFoundError:
        cookie_jar.save("cookies")
        return

    for cookie in cookie_jar:
        client.rest_client.cookie_jar.set_cookie(cookie)


def remove_cookies(filename: str = "cookies"):
    """
    remove cookies file
    """
    if Path(filename).exists:
        Path(filename).unlink()
