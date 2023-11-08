from typing import Awaitable, Callable, cast

from nonebot.utils import run_sync
from vrchatapi import AuthenticationApi
from vrchatapi.exceptions import ApiException, UnauthorizedException
from vrchatapi.models.current_user import CurrentUser
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

from .client import PLAYER_PATH, LoginInfo, get_client, save_client_cookies


class TwoFactorAuthError(Exception):
    def __init__(self, verify_func: Callable[[str], Awaitable[CurrentUser]]) -> None:
        """
        2FA 验证错误，当需要进行 2FA 验证时抛出

        Args:
            verify_func: 一个接受验证码作为参数的异步函数，调用后继续登录流程，并返回用户信息
        """
        super().__init__()
        self.verify_func = verify_func


async def login_via_password(
    session_id: str,
    username: str,
    password: str,
) -> CurrentUser:
    """
    使用用户名和密码登录

    Args:
        session_id: 用户 SessionID
        username: 用户名或邮箱
        password: 明文密码

    Raises:
        ApiException: API 调用异常
        TypeError: 服务器返回的 2FA 类型解析失败
        TwoFactorAuthError: 需要进行 2FA 验证，捕获后调用 `.verify_func()` 继续登录流程

    Returns:
        当前登录用户信息
    """

    client = await get_client(
        session_id=session_id,
        login_info=LoginInfo(username=username, password=password),
    )
    api = AuthenticationApi(client)

    def save_user_info():
        """保存用户登录信息"""
        info_path = PLAYER_PATH / f"{session_id}.json"
        info_path.write_text(
            LoginInfo(username=username, password=password).json(),
            encoding="utf-8",
        )
        save_client_cookies(client, session_id)

    try:
        # 调用 getCurrentUser 时，如果用户未登录，则会向服务器请求登录
        current_user = await cast(
            Awaitable[CurrentUser],
            run_sync(api.get_current_user)(),
        )

    except UnauthorizedException as e:
        # 服务器返回了非 200 状态码，则 API 调用出错，新建一个 ApiException 抛出
        if e.status != 200:
            exc = ApiException(e.status, e.reason)
            exc.body = e.body
            exc.headers = e.headers
            raise exc from e

        # 状态码为 200 时，则说明需要进行 2FA 验证
        if not (isinstance(e.reason, str) and "2 Factor Authentication" in e.reason):
            raise TypeError(f"Unknown Reason: {e.reason}") from e
        two_fa_email = "Email 2 Factor Authentication" in e.reason

        # 定义一个用于提交 2FA 验证码并继续登录流程的闭包函数
        async def verify_two_fa(auth_code: str) -> CurrentUser:
            if two_fa_email:
                await run_sync(api.verify2_fa_email_code)(
                    two_factor_email_code=TwoFactorEmailCode(auth_code),
                )
            else:
                await run_sync(api.verify2_fa)(
                    two_factor_auth_code=TwoFactorAuthCode(auth_code),
                )

            current_user = await cast(
                Awaitable[CurrentUser],
                run_sync(api.get_current_user)(),
            )
            save_user_info()
            return current_user

        raise TwoFactorAuthError(verify_two_fa) from e

    # 未抛出错误
    save_user_info()
    return current_user
