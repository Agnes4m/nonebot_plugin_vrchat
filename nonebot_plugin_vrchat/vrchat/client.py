# 引入 random 模块，用于生成随机数等需要随机操作的地方
import random

# 引入 http.cookiejar 模块的 LWPCookieJar 类，用于处理和存储 cookie 信息
from http.cookiejar import LWPCookieJar

# 引入 pathlib 模块的 Path 类，用于处理文件路径
from pathlib import Path

# 引入 typing 模块的 Optional 类，用于定义可能为空的类型注解
from typing import Optional

# 引入 pydantic 模块的 BaseModel 类，用于定义数据模型
from pydantic import BaseModel

# 引入 vrchatapi 模块的 ApiClient 和 Configuration 类，用于与 vrchatapi 的交互和配置
from vrchatapi import ApiClient, Configuration

# 从当前包的 config 模块中引入 config，这个应该是配置文件，包含一些设置和参数
from ..config import config

# 利用前面引入的 Path 类，根据 config 中的 vrc_path 和 "player" 路径创建 PLAYER_PATH 变量，如果路径不存在则创建
PLAYER_PATH = config.vrc_path / "player"
# 利用 Path 类的 mkdir 方法，创建父目录（如果需要）和存在时跳过（exist_ok=True），确保了路径的存在
PLAYER_PATH.mkdir(parents=True, exist_ok=True)


# 定义一个自定义异常类 NotLoggedInError，表示未登录错误，这在验证登录信息时会用到
class NotLoggedInError(Exception):
    pass


# 使用 BaseModel 定义一个 LoginInfo 类，这个类有两个字段，分别是 username 和 password，表示登录信息
class LoginInfo(BaseModel):
    username: str
    password: str


# 定义一个函数 save_client_cookies，这个函数的作用是保存 API 客户端的 cookie 信息
def save_client_cookies(client: ApiClient, session_id: str):
    # 根据 PLAYER_PATH 和 session_id 创建一个路径
    path = PLAYER_PATH / f"{session_id}.cookies"

    # 创建一个 LWPCookieJar 实例，并用该实例保存 cookie 信息
    cookie_jar = LWPCookieJar(filename=path)
    for cookie in client.rest_client.cookie_jar:
        cookie_jar.set_cookie(cookie)

    # 保存 cookie 信息到文件
    cookie_jar.save()


# 定义一个函数 load_cookies_to_client，这个函数的作用是加载已经保存的 cookie 信息到 API 客户端
def load_cookies_to_client(client: ApiClient, session_id: str):
    # 根据 PLAYER_PATH 和 session_id 创建一个路径
    path = PLAYER_PATH / f"{session_id}.cookies"
    # 如果路径不存在则直接返回，不需要加载 cookie
    if not path.exists():
        return

    # 创建一个 LWPCookieJar 实例，并从文件中加载 cookie 信息
    cookie_jar = LWPCookieJar(filename=path)
    cookie_jar.load()

    # 将加载的 cookie 信息设置到 API 客户端的 cookie jar 中
    for cookie in cookie_jar:
        client.rest_client.cookie_jar.set_cookie(cookie)


# 定义一个函数 remove_cookies，这个函数的作用是删除已经保存的 cookie 信息
def remove_cookies(session_id: str):
    # 根据 PLAYER_PATH 和 session_id 创建一个路径
    path = PLAYER_PATH / f"{session_id}.cookies"
    # 如果路径存在则删除文件，即删除 cookie 信息
    if path.exists():
        path.unlink()


# 定义一个函数 get_login_info，这个函数的作用是获取登录信息，如果登录信息不存在则抛出 NotLoggedInError 异常
def get_login_info(session_id: str) -> LoginInfo:
    # 根据 PLAYER_PATH 和 session_id 创建一个路径
    info_path = PLAYER_PATH / f"{session_id}.json"
    cookie_path = PLAYER_PATH / f"{session_id}.cookies"
    # 如果 info_path 和 cookie_path 都存在则读取并解析 info_path 的内容为 LoginInfo 对象，然后返回该对象
    if not (info_path.exists() and cookie_path.exists()):
        raise NotLoggedInError
    return LoginInfo.parse_raw(info_path.read_text(encoding="utf-8"))


def get_random_cookie() -> Optional[Path]:
    # 寻找 PLAYER_PATH 目录下所有 .cookies 文件
    cookies = list(PLAYER_PATH.glob("*.cookies"))
    # 如果有 .cookies 文件，那么随机选择一个并返回
    if cookies:
        return random.choice(cookies)
    # 如果没有 .cookies 文件，返回 None
    return None


def get_client(session_id: str, login_info: Optional[LoginInfo] = None) -> ApiClient:
    # 如果 login_info 参数为 None，那么通过 session_id 获取登录信息
    login_info = login_info or get_login_info(session_id)
    # 根据登录信息创建 Configuration 实例
    configuration = Configuration(
        username=login_info.username,
        password=login_info.password,
    )
    # 根据 Configuration 实例创建 ApiClient 实例
    client = ApiClient(configuration)
    # 加载已经保存的 cookie 信息到 ApiClient
    load_cookies_to_client(client, session_id)
    # 返回 ApiClient 实例
    return client


def random_client() -> ApiClient:
    # 随机获取一个 .cookies 文件路径
    cookie_path = get_random_cookie()
    # 如果不存在 .cookies 文件，那么抛出 NotLoggedInError 异常
    if not cookie_path:
        raise NotLoggedInError
    # 根据 .cookies 文件路径的 stem（即去除 .cookies 后缀的文件名）获取登录信息，并返回对应的 ApiClient 实例
    return get_client(cookie_path.stem)


def get_or_random_client(session_id: str) -> ApiClient:
    try:
        # 尝试获取已有的 ApiClient 实例
        return get_client(session_id)
    # 如果出现 NotLoggedInError 异常，那么随机获取一个 ApiClient 实例
    except NotLoggedInError:
        return random_client()
